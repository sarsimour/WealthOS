from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    CRYPTO = "CRYPTO"
    EQUITY = "EQUITY"
    FIXED_INCOME = "FIXED_INCOME"
    CURRENCY = "CURRENCY"
    FUND = "FUND"
    COMMODITY = "COMMODITY"
    DERIVATIVE = "DERIVATIVE"
    ALTERNATIVE = "ALTERNATIVE"


def generate_internal_id(
    asset_class: AssetClass, identifier: str
) -> str:
    """Generates a somewhat predictable internal ID."""
    return f"{asset_class.value.lower()}_{identifier.lower().replace(' ', '_')}"


class BaseAsset(BaseModel):
    internal_id: str = Field(
        ..., description="Unique internal identifier for the asset"
    )
    asset_class: AssetClass = Field(
        ...,
        description="The class of the asset (e.g., EQUITY, CRYPTO)",
    )
    name: str = Field(
        ...,
        description="Common name of the asset (e.g., Bitcoin, Apple Inc.)",
    )
    identifiers: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Dictionary of standard identifiers (e.g., {'symbol': 'BTC'}, "
            "{'ticker': 'AAPL', 'isin': '...'}) "
        ),
    )

    model_config = {"from_attributes": True}


class Crypto(BaseAsset):
    asset_class: AssetClass = Field(
        default=AssetClass.CRYPTO, frozen=True
    )
    # Add any crypto-specific fields here if needed in the future

    @classmethod
    def create(cls, name: str, symbol: str):
        """Helper method to create a Crypto asset instance."""
        internal_id = generate_internal_id(AssetClass.CRYPTO, symbol)
        identifiers = {"symbol": symbol.upper()}
        return cls(
            internal_id=internal_id,
            name=name,
            identifiers=identifiers,
        )


# Example Usage:
# btc_asset = Crypto.create(name="Bitcoin", symbol="BTC")
# print(btc_asset)
# >>> internal_id='crypto_btc' asset_class=<AssetClass.CRYPTO: 'CRYPTO'>
# >>> name='Bitcoin' identifiers={'symbol': 'BTC'}

# We can define Stock(BaseAsset), Bond(BaseAsset), etc. here later
