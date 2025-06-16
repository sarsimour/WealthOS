from fastapi import APIRouter, Depends, Query, Request

# Import the cache decorator
from fastapi_cache.decorator import cache

# Import the new dependency function
from app.services.price_service import get_price_provider

# Import the protocol for type hinting
from app.services.protocols import PriceProvider
from app.schemas.prices import PriceResponse

# Import the rate limiter dependency
# from fastapi_limiter.depends import RateLimiter

router = APIRouter()


@router.get(
    "/crypto/{base_asset_id}",
    response_model=PriceResponse,
    summary="Get Current Cryptocurrency Price",
    description="Fetches the current price for a given cryptocurrency identifier (e.g., 'BTC') via the configured provider.",
    # Add the rate limiter dependency
    # dependencies=[Depends(RateLimiter(times=10, minutes=1))],
)
# Add the cache decorator with a 60-second expiry
# @cache(expire=60)
async def get_crypto_price(
    request: Request,
    base_asset_id: str,
    vs_currency: str = Query(
        default="usd",
        description="The target quote currency (e.g., 'usd', 'eur', 'usdt')",
    ),
    price_provider: PriceProvider = Depends(get_price_provider),
):
    """
    Endpoint to retrieve the current price of a specific cryptocurrency.
    (Cached for 60 seconds)
    """
    # Log which provider is being used (optional)
    print(f"Using price provider: {type(price_provider).__name__}")
    print(
        f"Fetching price for {base_asset_id} in {vs_currency} (cache miss or expired - provider will be called)"
    )

    # The provider implementation handles API calls and errors
    price = await price_provider.get_price(
        base_asset_id=base_asset_id, quote_currency=vs_currency
    )

    return PriceResponse(
        identifier=base_asset_id, currency=vs_currency.lower(), price=price
    )


@router.get(
    "/bitcoin/full",
    summary="Get Full Bitcoin Data",
    description="Fetches current Bitcoin price and historical data from CoinGecko",
    # dependencies=[Depends(RateLimiter(times=5, minutes=1))],
)
# @cache(expire=60)
async def get_bitcoin_full_data(
    request: Request,
    vs_currency: str = Query(default="usd", description="The target quote currency"),
    days: int = Query(
        default=1, description="Number of days of historical data", ge=1, le=365
    ),
    price_provider: PriceProvider = Depends(get_price_provider),
):
    """
    Endpoint to retrieve comprehensive Bitcoin data including current price and historical data.
    (Cached for 60 seconds)
    """
    print(f"Using price provider: {type(price_provider).__name__}")
    print(f"Fetching full Bitcoin data for {days} days in {vs_currency}")

    # Get current price
    current_price = await price_provider.get_price(
        base_asset_id="bitcoin", quote_currency=vs_currency
    )

    # Get historical data if provider supports it
    historical_data = []
    if hasattr(price_provider, "get_historical_data"):
        try:
            historical_data = await price_provider.get_historical_data(
                base_asset_id="bitcoin", quote_currency=vs_currency, days=days
            )
        except Exception as e:
            print(f"Failed to get historical data: {e}")
            # Continue without historical data

    # Calculate 24h change if we have enough data
    price_change_24h = 0.0
    price_change_percent_24h = 0.0
    high_24h = current_price
    low_24h = current_price

    if historical_data and len(historical_data) > 0:
        # Get price from 24 hours ago
        twenty_four_hours_ago = (
            historical_data[0]["price"] if historical_data else current_price
        )
        price_change_24h = current_price - twenty_four_hours_ago
        price_change_percent_24h = (
            (price_change_24h / twenty_four_hours_ago) * 100
            if twenty_four_hours_ago != 0
            else 0
        )

        # Calculate 24h high and low
        prices = [point["price"] for point in historical_data]
        high_24h = max(prices + [current_price])
        low_24h = min(prices + [current_price])

    return {
        "symbol": "BTC",
        "current_price": current_price,
        "price_change_24h": price_change_24h,
        "price_change_percent_24h": price_change_percent_24h,
        "high_24h": high_24h,
        "low_24h": low_24h,
        "historical_data": historical_data,
        "currency": vs_currency.lower(),
        "last_updated": "now",
    }


@router.get(
    "/stock/{symbol}",
    response_model=PriceResponse,
    summary="Get Latest Stock Price",
    description="Fetches the latest price for a given stock symbol (e.g., 'IBM') via the configured provider.",
    # dependencies=[Depends(RateLimiter(times=10, minutes=1))],
)
# @cache(expire=60)
async def get_stock_price(
    request: Request,
    symbol: str,
    price_provider: PriceProvider = Depends(get_price_provider),
):
    """
    Endpoint to retrieve the latest price of a specific stock.
    (Cached for 60 seconds)
    """
    # For stocks, the quote currency is often implicitly USD with free APIs.
    # The provider handles the logic.
    quote_currency = "usd"

    print(f"Using price provider: {type(price_provider).__name__}")
    print(
        f"Fetching price for {symbol} (cache miss or expired - provider will be called)"
    )

    price = await price_provider.get_price(
        base_asset_id=symbol, quote_currency=quote_currency
    )

    return PriceResponse(identifier=symbol, currency=quote_currency, price=price)


# TODO:
# 1. Implement mapping from our internal asset IDs (e.g., 'crypto_btc') to provider IDs ('bitcoin' or 'BTC').
# 2. ~~Add caching using fastapi-cache~~ (Done - In-Memory)
# 3. Add authentication/authorization if needed.
# 4. Consider using Redis backend for caching in production.
# 5. ~~Implement rate limiting for this endpoint.~~ (Done - 10/min)
# 6. Add configuration for price provider selection.
# 7. Ensure Redis server is running for rate limiting to work.
