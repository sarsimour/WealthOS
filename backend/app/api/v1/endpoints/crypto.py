from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

# Change to absolute imports
from app.schemas.market_data import MarketDataPoint
from app.services.crypto_market_data import get_latest_crypto_price

router = APIRouter()

# Define a mapping from user-facing symbols (like 'btc')
# to CoinGecko IDs (like 'bitcoin') if needed.
# Simple case for now: assume symbol maps directly.
COINGECKO_ID_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    # Add more mappings as needed
}

# Map internal asset name
ASSET_NAME_MAP = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
}


@router.get(
    "/{asset_symbol}/market_data/latest",
    response_model=MarketDataPoint,
    summary="Get Latest Market Data for a Crypto Asset",
    description=(
        "Fetches the latest market data point (usually price) for a given "
        "cryptocurrency symbol from the configured provider (e.g., CoinGecko)."
    ),
    tags=["Crypto Market Data"],
)
async def read_latest_crypto_market_data(
    asset_symbol: Annotated[
        str,
        Path(
            description=(
                "The symbol of the cryptocurrency (e.g., 'btc', 'eth'). "
                "Case-insensitive."
            )
        ),
    ],
    currency: Annotated[
        str,
        Query(
            description=(
                "The currency to get the price in (e.g., 'USD', 'EUR'). "
                "Case-insensitive."
            )
        ),
    ] = "USD",
):
    """Retrieves the latest market data point for the specified crypto asset."""
    symbol_lower = asset_symbol.lower()
    currency_lower = currency.lower()

    # Use the mapping to get the ID CoinGecko expects
    coingecko_id = COINGECKO_ID_MAP.get(
        symbol_lower, symbol_lower
    )  # Default to symbol if not in map
    asset_name = ASSET_NAME_MAP.get(coingecko_id)

    try:
        market_data = await get_latest_crypto_price(
            asset_symbol=coingecko_id,  # Use the mapped ID
            currency=currency_lower,
            asset_name=asset_name,
        )
        return market_data
    except HTTPException as e:
        # Re-raise HTTPException to let FastAPI handle it
        raise e
    except Exception as e:
        # Catch unexpected errors from the service if not already HTTPExceptions
        # (Though the service tries to convert them)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {e}",
        )
