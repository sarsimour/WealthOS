from typing import Any, Dict, List

import httpx
from fastapi import HTTPException, status

try:
    from pycoingecko import CoinGeckoAPI

    PYCOINGECKO_AVAILABLE = True
except ImportError:
    CoinGeckoAPI = None
    PYCOINGECKO_AVAILABLE = False

# Import the protocol
from app.services.protocols import PriceProvider

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoProvider(PriceProvider):  # Implement the protocol
    """Fetches cryptocurrency prices using the CoinGecko API."""

    def __init__(self):
        self.cg = CoinGeckoAPI() if PYCOINGECKO_AVAILABLE else None

    async def get_price(self, base_asset_id: str, quote_currency: str) -> float:
        """
        Fetches the current price from CoinGecko.

        Args:
            base_asset_id: The CoinGecko ID (e.g., 'bitcoin').
            quote_currency: The quote currency symbol (e.g., 'usd').

        Returns:
            The current price.

        Raises:
            HTTPException: If the API request fails or the price cannot be found.
        """
        # Map common symbols to CoinGecko IDs
        symbol_to_id = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "bitcoin": "bitcoin",
            "ethereum": "ethereum",
        }

        coingecko_id = symbol_to_id.get(base_asset_id.lower(), base_asset_id.lower())
        target_currency = quote_currency.lower()

        try:
            if PYCOINGECKO_AVAILABLE and self.cg:
                # Use pycoingecko library for better reliability
                data = self.cg.get_price(
                    ids=coingecko_id, vs_currencies=target_currency
                )

                if (
                    not data
                    or coingecko_id not in data
                    or target_currency not in data[coingecko_id]
                ):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"CoinGecko: Price data not found for ID '{coingecko_id}' in currency '{target_currency}'",
                    )

                return float(data[coingecko_id][target_currency])
            else:
                # Fallback to direct HTTP API call
                return await self._get_price_http(coingecko_id, target_currency)

        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"CoinGecko API error: {str(e)}",
            ) from e

    async def get_historical_data(
        self, base_asset_id: str, quote_currency: str, days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Fetches historical price data from CoinGecko.

        Args:
            base_asset_id: The CoinGecko ID (e.g., 'bitcoin')
            quote_currency: The quote currency symbol (e.g., 'usd')
            days: Number of days of historical data

        Returns:
            List of price data points with timestamp and price
        """
        symbol_to_id = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "bitcoin": "bitcoin",
            "ethereum": "ethereum",
        }

        coingecko_id = symbol_to_id.get(base_asset_id.lower(), base_asset_id.lower())
        target_currency = quote_currency.lower()

        try:
            if PYCOINGECKO_AVAILABLE and self.cg:
                # Get historical data using pycoingecko
                data = self.cg.get_coin_market_chart_by_id(
                    id=coingecko_id, vs_currency=target_currency, days=days
                )

                if not data or "prices" not in data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"CoinGecko: Historical data not found for '{coingecko_id}'",
                    )

                # Convert to our format
                historical_data = []
                for price_point in data["prices"]:
                    timestamp_ms, price = price_point
                    historical_data.append(
                        {"timestamp": int(timestamp_ms), "price": float(price)}
                    )

                return historical_data
            else:
                # Fallback to HTTP API
                return await self._get_historical_data_http(
                    coingecko_id, target_currency, days
                )

        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"CoinGecko API error: {str(e)}",
            ) from e

    async def _get_price_http(self, coingecko_id: str, target_currency: str) -> float:
        """Fallback HTTP method for getting current price."""
        url = f"{COINGECKO_API_URL}/simple/price"
        params = {
            "ids": coingecko_id,
            "vs_currencies": target_currency,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if (
                    not data
                    or coingecko_id not in data
                    or target_currency not in data[coingecko_id]
                ):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"CoinGecko: Price data not found for ID '{coingecko_id}' in currency '{target_currency}'",
                    )

                price = data[coingecko_id][target_currency]
                return float(price)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"CoinGecko: Asset ID '{coingecko_id}' or currency '{target_currency}' not found.",
                    ) from e
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"CoinGecko API ({e.request.url}) failed: {e.response.status_code}",
                ) from e
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"CoinGecko API connection error: {e}",
                ) from e

    async def _get_historical_data_http(
        self, coingecko_id: str, target_currency: str, days: int
    ) -> List[Dict[str, Any]]:
        """Fallback HTTP method for getting historical data."""
        url = f"{COINGECKO_API_URL}/coins/{coingecko_id}/market_chart"
        params = {
            "vs_currency": target_currency,
            "days": days,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data or "prices" not in data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"CoinGecko: Historical data not found for '{coingecko_id}'",
                    )

                historical_data = []
                for price_point in data["prices"]:
                    timestamp_ms, price = price_point
                    historical_data.append(
                        {"timestamp": int(timestamp_ms), "price": float(price)}
                    )

                return historical_data

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"CoinGecko API failed: {e.response.status_code}",
                ) from e
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"CoinGecko API connection error: {e}",
                ) from e
