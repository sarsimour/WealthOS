from datetime import datetime
from typing import List, Optional

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


class HistoricalPricePoint(BaseModel):
    """Individual price point in historical data"""

    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    price: float = Field(..., description="Price at the given timestamp")
    volume: Optional[float] = Field(None, description="Trading volume (if available)")


class HistoricalDataMetadata(BaseModel):
    """Metadata for historical price data"""

    total_points: int = Field(..., description="Total number of data points")
    start_time: datetime = Field(..., description="Start time of the data range")
    end_time: datetime = Field(..., description="End time of the data range")
    interval: str = Field(..., description="Data interval (e.g., '1h', '1d')")


class HistoricalPriceResponse(BaseModel):
    """Response model for historical price data"""

    symbol: str = Field(..., description="Asset symbol (e.g., 'BTC')")
    currency: str = Field(..., description="Quote currency")
    period: str = Field(..., description="Time period requested (e.g., '7d', '30d')")
    interval: str = Field(..., description="Data interval")
    data: List[HistoricalPricePoint] = Field(
        ..., description="List of historical price points"
    )
    metadata: HistoricalDataMetadata = Field(..., description="Metadata about the data")


class FullBitcoinDataResponse(BaseModel):
    """Comprehensive Bitcoin data response"""

    symbol: str = Field(default="BTC", description="Asset symbol")
    current_price: float = Field(..., description="Current Bitcoin price")
    price_change_24h: float = Field(
        ..., description="24h price change in absolute terms"
    )
    price_change_percent_24h: float = Field(
        ..., description="24h price change in percentage"
    )
    high_24h: float = Field(..., description="24h high price")
    low_24h: float = Field(..., description="24h low price")
    historical_data: List[HistoricalPricePoint] = Field(
        ..., description="Historical price data"
    )
    currency: str = Field(..., description="Quote currency")
    last_updated: str = Field(..., description="Last update timestamp")
