import time

from fastapi import APIRouter, Depends, HTTPException

from app.services.price_service import get_price_provider
from app.services.protocols import PriceProvider

router = APIRouter(prefix="/price", tags=["price"])


@router.get("/{base_asset}/{quote_currency}")
async def get_price(
    base_asset: str,
    quote_currency: str,
    provider: PriceProvider = Depends(get_price_provider),
):
    """Get current price for a trading pair."""
    try:
        price = await provider.get_price(base_asset, quote_currency)
        return {
            "symbol": f"{base_asset}{quote_currency}",
            "price": str(price),
            "timestamp": int(time.time()),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
