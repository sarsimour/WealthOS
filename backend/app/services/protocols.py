from typing import Protocol


class PriceProvider(Protocol):
    # A simple placeholder docstring
    """Interface for price providers."""

    async def get_price(self, base_asset_id: str, quote_currency: str) -> float:
        # Implementations should raise ValueError or HTTPException on failure
        ...
