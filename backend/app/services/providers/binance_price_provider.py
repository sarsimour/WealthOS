import httpx
from fastapi import HTTPException, status

# Import the protocol
from app.services.protocols import PriceProvider

# Binance API configuration
BINANCE_API_URL = "https://api.binance.com/api/v3"


class BinanceProvider(PriceProvider):  # Implement the protocol
    """Fetches cryptocurrency prices using the Binance API with internal rate limiting."""

    def _format_symbol(self, base_asset_id: str, quote_currency: str) -> str:
        """Formats the asset IDs into a Binance symbol (e.g., BTCUSDT)."""
        # Basic formatting, may need refinement for specific assets
        # Handle common case USD -> USDT for Binance
        quote = quote_currency.upper()
        if quote == "USD":
            quote = "USDT"  # Default to USDT pair if USD is requested

        return f"{base_asset_id.upper()}{quote}"

    async def _make_binance_request(self, url: str, params: dict):
        """Internal method to make request to Binance."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Let caller handle HTTPStatusError
            return response.json()

    async def get_price(self, base_asset_id: str, quote_currency: str) -> float:
        """
        Fetches the current price from Binance (rate-limited).

        Args:
            base_asset_id: The base asset symbol (e.g., 'BTC').
            quote_currency: The quote currency symbol (e.g., 'USD', 'USDT').

        Returns:
            The current price.

        Raises:
            HTTPException: If the API request fails or the price cannot be found.
            ValueError: If the symbol format is invalid for Binance.
        """
        try:
            symbol = self._format_symbol(base_asset_id, quote_currency)
        except Exception as e:
            raise ValueError(
                f"Could not format Binance symbol for {base_asset_id}/{quote_currency}: {e}"
            ) from e

        url = f"{BINANCE_API_URL}/ticker/price"
        params = {"symbol": symbol}

        try:
            # Call the internal method
            data = await self._make_binance_request(url, params)

            if "price" not in data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Binance: Price data missing in response for symbol '{symbol}'",
                )

            price_str = data["price"]
            return float(price_str)
        except httpx.HTTPStatusError as e:
            # Handle specific Binance error codes if needed from e.response.json()
            if e.response.status_code == 400:
                raise ValueError(
                    f"Binance: Invalid symbol format or symbol does not exist: '{symbol}'. {e.response.text}"
                ) from e
            elif e.response.status_code == 429:  # External rate limit exceeded
                # Log this specific external limit hit
                print(
                    f"External Binance rate limit hit for symbol {symbol}: {e.response.text}"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="External Binance API rate limit exceeded. Please try again later.",
                ) from e
            # Log other errors
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Binance API ({e.request.url}) failed: {e.response.status_code}. {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            # Log the error str(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Binance API connection error: {e}",
            ) from e
        except (KeyError, ValueError, TypeError) as e:
            # Log the error str(e) and potentially the received data
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Binance API: Error processing price data for '{symbol}' - {e}.",
            ) from e
