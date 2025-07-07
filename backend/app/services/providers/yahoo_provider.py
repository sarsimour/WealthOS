from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException

from app.services.protocols import PriceProvider


class YahooFinanceProvider(PriceProvider):
    """Yahoo Finance provider for Bitcoin and other crypto prices."""

    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    def _get_symbol(self, base_asset_id: str, quote_currency: str) -> str:
        """Convert asset ID to Yahoo Finance symbol."""
        symbol_map = {
            ("btc", "usd"): "BTC-USD",
            ("bitcoin", "usd"): "BTC-USD",
            ("eth", "usd"): "ETH-USD",
            ("ethereum", "usd"): "ETH-USD",
        }

        key = (base_asset_id.lower(), quote_currency.lower())
        return symbol_map.get(key, f"{base_asset_id.upper()}-{quote_currency.upper()}")

    async def get_price(self, base_asset_id: str, quote_currency: str) -> float:
        """Get current price from Yahoo Finance."""
        symbol = self._get_symbol(base_asset_id, quote_currency)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/{symbol}"
                params = {"interval": "1m", "range": "1d", "includePrePost": "true"}

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if "chart" not in data or not data["chart"]["result"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Yahoo Finance: No data found for {symbol}",
                    )

                result = data["chart"]["result"][0]
                meta = result["meta"]

                if "regularMarketPrice" not in meta:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Yahoo Finance: No current price for {symbol}",
                    )

                return float(meta["regularMarketPrice"])

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Yahoo Finance API failed: {e.response.status_code}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Yahoo Finance error: {str(e)}"
            )

    async def get_historical_data(
        self, base_asset_id: str, quote_currency: str, days: int = 1
    ) -> List[Dict[str, Any]]:
        """Get historical data from Yahoo Finance."""
        symbol = self._get_symbol(base_asset_id, quote_currency)

        # Calculate timestamp range
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.base_url}/{symbol}"
                params = {
                    "period1": start_time,
                    "period2": end_time,
                    "interval": "1h" if days <= 7 else "1d",
                    "includePrePost": "false",
                }

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if "chart" not in data or not data["chart"]["result"]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Yahoo Finance: No historical data for {symbol}",
                    )

                result = data["chart"]["result"][0]
                timestamps = result["timestamp"]
                quotes = result["indicators"]["quote"][0]
                closes = quotes["close"]

                historical_data = []
                for i, timestamp in enumerate(timestamps):
                    if closes[i] is not None:  # Skip null values
                        historical_data.append(
                            {
                                "timestamp": int(
                                    timestamp * 1000
                                ),  # Convert to milliseconds
                                "price": float(closes[i]),
                            }
                        )

                return historical_data

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Yahoo Finance API failed: {e.response.status_code}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Yahoo Finance error: {str(e)}"
            )
