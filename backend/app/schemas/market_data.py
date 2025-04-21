from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# Assuming assets.py is in the same directory or path is configured
# from .assets import BaseAsset # Temporarily comment out until assets.py exists
# from .assets import Crypto  # Removed unused import F401

# Imports sorted


class MarketDataSource(str, Enum):
    COINGECKO = "coingecko"
    YAHOO_FINANCE = "yahoo_finance"
    INTERNAL = "internal_calculation"
    # Add more sources as needed


class PriceType(str, Enum):
    TRADE = "trade"
    BID = "bid"
    ASK = "ask"
    NET_ASSET_VALUE = "nav"
    MID = "mid"


class MarketDataPoint(BaseModel):
    asset_internal_id: str = Field(
        ...,
        description="Internal ID of the asset this data point belongs to",
    )
    timestamp: datetime = Field(
        ..., description="Timestamp for when the data point is valid"
    )
    source: MarketDataSource = Field(..., description="Source of the market data")
    currency: str = Field(
        ...,
        description="Currency of the price/value (e.g., USD, EUR)",
    )
    market: Optional[str] = Field(
        None,
        description="Specific market/exchange (e.g., NASDAQ, Binance)",
    )
    price_type: PriceType = Field(
        default=PriceType.TRADE,
        description="Type of price (trade, bid, ask, etc.)",
    )
    value: float = Field(
        ...,
        description="The numeric value of the data point (e.g., price)",
    )
    # Optional OHLCV fields
    open: Optional[float] = Field(None, description="Opening price for the period")
    high: Optional[float] = Field(None, description="Highest price for the period")
    low: Optional[float] = Field(None, description="Lowest price for the period")
    close: Optional[float] = Field(
        None,
        description="Closing price for the period (redundant if value is price)",
    )
    volume: Optional[float] = Field(None, description="Trading volume for the period")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "asset_internal_id": "crypto_btc",
                    "timestamp": "2023-10-27T10:00:00Z",
                    "source": "coingecko",
                    "currency": "USD",
                    "market": None,
                    "price_type": "trade",
                    "value": 65000.50,
                }
            ]
        },
    }


# We can add FundamentalDataPoint etc. later
