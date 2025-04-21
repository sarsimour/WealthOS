import logging
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException

from app.schemas.assets import (
    AssetClass,
    generate_internal_id,
)
from app.schemas.market_data import (
    MarketDataPoint,
    MarketDataSource,
    PriceType,
)

logger = logging.getLogger(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


async def get_latest_crypto_price(
    asset_symbol: str,
    currency: str,
    asset_name: str | None = None,  # Optional, helpful for creating the asset object
) -> MarketDataPoint:
    """Fetches the latest price for a cryptocurrency from CoinGecko."""

    # Basic validation
    asset_symbol = asset_symbol.lower()
    currency = currency.lower()
    # Map common symbols to coingecko IDs if necessary (e.g., BTC -> bitcoin)
    # For simplicity, assuming symbol matches coingecko ID for now
    coingecko_id = asset_symbol

    # Generate internal ID for the asset (used in MarketDataPoint)
    # We could fetch/cache the full asset details from a DB later
    internal_asset_id = generate_internal_id(AssetClass.CRYPTO, asset_symbol)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                COINGECKO_API_URL,
                params={
                    "ids": coingecko_id,
                    "vs_currencies": currency,
                },
            )
            response.raise_for_status()  # Raise exception for 4xx or 5xx status codes
            data = response.json()

    except httpx.RequestError as exc:
        logger.error(
            f"HTTP request error fetching {asset_symbol}/{currency} from CoinGecko: "
            f"{exc}"
        )
        raise HTTPException(
            status_code=503,
            detail=f"Error contacting external data provider: {exc}",
        ) from exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"HTTP status error fetching {asset_symbol}/{currency} from CoinGecko: "
            f"{exc}"
        )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"External data provider returned error: {exc.response.text}",
        ) from exc
    except Exception as exc:  # Capture exception in 'exc'
        logger.exception(
            f"Unexpected error fetching {asset_symbol}/{currency} from CoinGecko"
        )  # Log full traceback
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching external data.",
        ) from exc  # Use 'from exc' here as well

    # Process the response
    if coingecko_id not in data or currency not in data[coingecko_id]:
        logger.warning(
            f"CoinGecko response missing expected data for {asset_symbol}/{currency}. "
            f"Response: {data}"
        )
        raise HTTPException(
            status_code=404,
            detail=(
                f"Price data not found for {asset_symbol.upper()} in "
                f"{currency.upper()} from source."
            ),
        )

    price = data[coingecko_id][currency]
    if not isinstance(price, (int, float)):
        logger.error(
            "Invalid price type received from CoinGecko "
            f"for {asset_symbol}/{currency}: "
            f"{type(price)}, value: {price}"
        )
        raise HTTPException(
            status_code=500,
            detail="Invalid data format received from external provider.",
        )
    # Create the MarketDataPoint object
    market_data = MarketDataPoint(
        asset_internal_id=internal_asset_id,
        timestamp=datetime.now(timezone.utc),
        source=MarketDataSource.COINGECKO,
        currency=currency.upper(),
        price_type=PriceType.TRADE,
        value=float(price),
        market="spot",  # Adding required market parameter
        open=float(price),  # Using current price as open
        high=float(price),  # Using current price as high
        low=float(price),  # Using current price as low
        close=float(price),  # Using current price as close
        volume=0.0,  # Setting volume to 0 since we don't have this data
    )

    return market_data
