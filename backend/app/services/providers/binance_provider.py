import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import httpx
from fastapi import HTTPException

# Import the protocol
from app.services.protocols import PriceProvider


class BinanceProvider(PriceProvider):
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.base_url = "https://api.binance.com"
        self.api_key = api_key
        self.api_secret = api_secret

    def _format_symbol(self, base_asset_id: str, quote_currency: str) -> str:
        """Formats the asset IDs into a Binance symbol (e.g., BTCUSDT)."""
        quote = quote_currency.upper()
        if quote == "USD":
            quote = "USDT"
        return f"{base_asset_id.upper()}{quote}"

    async def get_price(self, base_asset_id: str, quote_currency: str) -> float:
        """
        Fetches the current price from Binance asynchronously.
        """
        symbol = self._format_symbol(base_asset_id, quote_currency)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v3/ticker/price",
                    params={"symbol": symbol},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return float(data["price"])
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=404, detail=f"Symbol {symbol} not found on Binance"
                    )
                raise HTTPException(
                    status_code=503, detail=f"Binance API error: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching price from Binance: {str(e)}",
                )

    async def get_historical_data(
        self, base_asset_id: str, quote_currency: str, days: int
    ) -> List[Dict[str, Any]]:
        """
        Get historical crypto data from Binance asynchronously.
        """
        symbol = self._format_symbol(base_asset_id, quote_currency)
        start_dt = datetime.now(timezone.utc) - timedelta(days=days)
        start_ts = int(start_dt.timestamp() * 1000)

        # Determine interval based on days
        if days <= 1:
            interval = "15m"
        elif days <= 7:
            interval = "2h"
        elif days <= 30:
            interval = "8h"
        else:
            interval = "1d"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v3/klines",
                    params={
                        "symbol": symbol,
                        "interval": interval,
                        "startTime": start_ts,
                        "limit": 1000,
                    },
                    timeout=15.0,
                )
                response.raise_for_status()
                klines = response.json()

                if not klines:
                    return []

                # Format the data into the expected structure
                # Binance kline format: [open_time, open, high, low, close, ...]
                formatted_data = [
                    {"timestamp": int(kline[0]), "price": float(kline[4])}
                    for kline in klines
                ]
                return formatted_data
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=404, detail=f"Symbol {symbol} not found on Binance"
                    )
                raise HTTPException(
                    status_code=503, detail=f"Binance API error: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching historical data from Binance: {str(e)}",
                )
