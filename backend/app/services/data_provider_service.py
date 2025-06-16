import pandas as pd

from app.services.providers.akshare_provider import AkshareProvider
from app.services.providers.binance_provider import BinanceProvider
from app.services.providers.yfinance_provider import YFinanceProvider


class DataProviderService:
    def __init__(self):
        self._providers = {
            "akshare": AkshareProvider(),
            "yfinance": YFinanceProvider(),
            "binance": BinanceProvider(),
        }

    def get_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        market: str = "other",
        asset_type: str = "stock",
    ) -> pd.DataFrame:
        """
        Get data from the correct provider based on market and asset type.
        """
        if asset_type == "crypto":
            if market == "binance":
                return self._providers["binance"].get_crypto_data(
                    symbol, start_date, end_date
                )
            else:
                return self._providers["yfinance"].get_crypto_data(
                    symbol, start_date, end_date
                )

        if market == "cn":
            return self._providers["akshare"].get_stock_data(
                symbol, start_date, end_date
            )
        else:
            return self._providers["yfinance"].get_stock_data(
                symbol, start_date, end_date
            )
