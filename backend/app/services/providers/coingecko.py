import httpx
from fastapi import HTTPException, status

# Import the protocol
from app.services.protocols import PriceProvider

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoProvider(PriceProvider):  # Implement the protocol
    """Fetches cryptocurrency prices using the CoinGecko API."""

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
            ValueError: CoinGecko doesn't really have invalid ID formats,
                        but keeping for protocol consistency. Errors manifest as 404.
        """
        # CoinGecko uses specific IDs (like 'bitcoin')
        coingecko_id = base_asset_id.lower()
        target_currency = quote_currency.lower()

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
                # Distinguish between 404 (handled above) and other errors
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"CoinGecko: Asset ID '{coingecko_id}' or currency '{target_currency}' not found.",
                    ) from e
                # Log the error e.response.text
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"CoinGecko API ({e.request.url}) failed: {e.response.status_code}",
                ) from e
            except httpx.RequestError as e:
                # Log the error str(e)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"CoinGecko API connection error: {e}",
                ) from e
            except (KeyError, ValueError, TypeError) as e:
                # Log the error str(e) and potentially the received data
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"CoinGecko API: Error processing price data - {e}.",
                ) from e
