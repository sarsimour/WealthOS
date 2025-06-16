import os
import httpx
from fastapi import HTTPException, status
from app.services.protocols import PriceProvider

# It's recommended to load the API key from environment variables
# For example: ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
# For this example, we'll use "demo" as a fallback.
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"


class AlphaVantageProvider(PriceProvider):
    """Fetches stock prices using the Alpha Vantage API."""

    async def get_price(self, base_asset_id: str, quote_currency: str) -> float:
        """
        Fetches the latest price for a stock symbol from Alpha Vantage.

        Args:
            base_asset_id: The stock symbol (e.g., 'IBM').
            quote_currency: The quote currency. Alpha Vantage primarily returns in USD,
                            so this parameter is noted but may not alter the direct API call
                            if the endpoint doesn't support it for free tiers.

        Returns:
            The latest price of the stock.

        Raises:
            HTTPException: If the API request fails or the price cannot be found.
        """
        symbol = base_asset_id.upper()

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(ALPHA_VANTAGE_API_URL, params=params)
                response.raise_for_status()
                data = response.json()

                global_quote = data.get("Global Quote")
                if not global_quote:
                    # The API might return an empty object or a note about API usage.
                    note = data.get("Note")
                    if note:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Alpha Vantage API limit reached: {note}",
                        )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Alpha Vantage: Data not found for symbol '{symbol}'. Response: {data}",
                    )

                price_str = global_quote.get("05. price")
                if price_str is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Alpha Vantage: Price not found in response for '{symbol}'.",
                    )

                return float(price_str)

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Alpha Vantage API ({e.request.url}) failed: {e.response.status_code}",
                ) from e
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Alpha Vantage API connection error: {e}",
                ) from e
            except (ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Alpha Vantage API: Error processing price data - {e}.",
                ) from e
