from pydantic import BaseModel, Field


class PriceResponse(BaseModel):
    """Response model for asset price requests."""

    identifier: str = Field(
        ..., description="The identifier used for the price lookup (e.g., CoinGecko ID)"
    )
    currency: str = Field(
        ..., description="The currency the price is quoted in (e.g., usd)"
    )
    price: float = Field(..., description="The current price of the asset")
