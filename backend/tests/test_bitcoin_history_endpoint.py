import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.main import app
from app.services.providers.binance_provider import BinanceProvider

client = TestClient(app)


class TestBitcoinHistoryEndpoint:
    """Test suite for Bitcoin history endpoint"""

    @pytest.fixture
    def mock_historical_data(self):
        """Mock historical data for testing"""
        base_timestamp = int(
            datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000
        )
        return [
            {
                "timestamp": base_timestamp + (i * 3600000),  # Hourly intervals
                "price": 45000.0 + (i * 100),  # Incrementing price
                "volume": 1000000.0 + (i * 1000),
            }
            for i in range(24)  # 24 hours of data
        ]

    @pytest.fixture
    def mock_binance_provider(self, mock_historical_data):
        """Mock Binance provider for testing"""
        mock_provider = AsyncMock(spec=BinanceProvider)
        mock_provider.get_historical_data = AsyncMock(return_value=mock_historical_data)
        mock_provider.get_price = AsyncMock(return_value=47400.0)  # Current price
        return mock_provider

    def test_bitcoin_history_valid_periods(
        self, mock_binance_provider, mock_historical_data
    ):
        """Test Bitcoin history endpoint with valid periods"""
        with patch(
            "app.services.price_service.get_price_provider",
            return_value=mock_binance_provider,
        ):
            # Test each valid period
            valid_periods = ["1d", "7d", "30d", "90d", "1y"]

            for period in valid_periods:
                response = client.get(f"/api/v1/prices/bitcoin/history?period={period}")

                assert response.status_code == 200
                data = response.json()

                # Validate response structure
                assert data["symbol"] == "BTC"
                assert data["currency"] == "usd"
                assert data["period"] == period
                assert "interval" in data
                assert "data" in data
                assert "metadata" in data

                # Validate data points
                assert len(data["data"]) == len(mock_historical_data)

                # Validate first data point
                first_point = data["data"][0]
                assert "timestamp" in first_point
                assert "price" in first_point
                assert first_point["price"] == 45000.0

                # Validate metadata
                metadata = data["metadata"]
                assert metadata["total_points"] == len(mock_historical_data)
                assert "start_time" in metadata
                assert "end_time" in metadata

    def test_bitcoin_history_invalid_period(self):
        """Test Bitcoin history endpoint with invalid period"""
        response = client.get("/api/v1/prices/bitcoin/history?period=invalid")

        assert response.status_code == 422  # Validation error from regex pattern

    def test_bitcoin_history_invalid_interval(self):
        """Test Bitcoin history endpoint with invalid interval"""
        response = client.get(
            "/api/v1/prices/bitcoin/history?period=7d&interval=invalid"
        )

        assert response.status_code == 422  # Validation error from regex pattern

    def test_bitcoin_history_custom_currency(
        self, mock_binance_provider, mock_historical_data
    ):
        """Test Bitcoin history endpoint with custom currency"""
        with patch(
            "app.services.price_service.get_price_provider",
            return_value=mock_binance_provider,
        ):
            response = client.get(
                "/api/v1/prices/bitcoin/history?period=7d&currency=eur"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["currency"] == "eur"

    def test_bitcoin_history_no_data(self):
        """Test Bitcoin history endpoint when no data is available"""
        mock_provider = AsyncMock(spec=BinanceProvider)
        mock_provider.get_historical_data = AsyncMock(return_value=[])

        with patch(
            "app.services.price_service.get_price_provider", return_value=mock_provider
        ):
            response = client.get("/api/v1/prices/bitcoin/history?period=7d")

            assert response.status_code == 404
            assert "No historical data found" in response.json()["detail"]

    def test_bitcoin_history_provider_error(self):
        """Test Bitcoin history endpoint when provider throws error"""
        mock_provider = AsyncMock(spec=BinanceProvider)
        mock_provider.get_historical_data = AsyncMock(
            side_effect=Exception("Provider error")
        )

        with patch(
            "app.services.price_service.get_price_provider", return_value=mock_provider
        ):
            response = client.get("/api/v1/prices/bitcoin/history?period=7d")

            assert response.status_code == 500
            assert "Internal server error" in response.json()["detail"]

    def test_bitcoin_history_unsupported_provider(self):
        """Test Bitcoin history endpoint with provider that doesn't support historical data"""
        # Mock a provider without get_historical_data method
        mock_provider = AsyncMock()
        # Remove the method to simulate unsupported provider
        if hasattr(mock_provider, "get_historical_data"):
            delattr(mock_provider, "get_historical_data")

        with patch(
            "app.services.price_service.get_price_provider", return_value=mock_provider
        ):
            response = client.get("/api/v1/prices/bitcoin/history?period=7d")

            assert response.status_code == 503
            assert "Historical data not supported" in response.json()["detail"]

    def test_bitcoin_full_data_endpoint(
        self, mock_binance_provider, mock_historical_data
    ):
        """Test the full Bitcoin data endpoint"""
        with patch(
            "app.services.price_service.get_price_provider",
            return_value=mock_binance_provider,
        ):
            response = client.get("/api/v1/prices/bitcoin/full?days=1")

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            required_fields = [
                "symbol",
                "current_price",
                "price_change_24h",
                "price_change_percent_24h",
                "high_24h",
                "low_24h",
                "historical_data",
                "currency",
                "last_updated",
            ]

            for field in required_fields:
                assert field in data

            assert data["symbol"] == "BTC"
            assert data["current_price"] == 47400.0
            assert len(data["historical_data"]) == len(mock_historical_data)

            # Validate historical data structure
            first_point = data["historical_data"][0]
            assert "timestamp" in first_point
            assert "price" in first_point

    def test_interval_auto_selection(self):
        """Test automatic interval selection based on period"""
        from app.api.v1.endpoints.prices import _get_interval_for_period

        assert _get_interval_for_period("1d") == "15m"
        assert _get_interval_for_period("7d") == "2h"
        assert _get_interval_for_period("30d") == "8h"
        assert _get_interval_for_period("90d") == "1d"
        assert _get_interval_for_period("1y") == "1d"


if __name__ == "__main__":
    pytest.main([__file__])
