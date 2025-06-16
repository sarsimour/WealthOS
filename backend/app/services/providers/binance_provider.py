from datetime import datetime
from typing import Optional

import pandas as pd
from binance.spot import Spot


class BinanceProvider:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.client = Spot(api_key=api_key, api_secret=api_secret)

    def get_crypto_data(
        self, symbol: str, start_date: str, end_date: str, interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Get historical crypto data from Binance.
        """
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

            klines = self.client.klines(
                symbol=symbol.upper(),
                interval=interval,
                startTime=start_ts,
                endTime=end_ts,
                limit=1000,  # Max limit
            )

            if not klines:
                return pd.DataFrame()

            df = pd.DataFrame(
                klines,
                columns=[
                    "Open Time",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "Close Time",
                    "Quote Asset Volume",
                    "Number of Trades",
                    "Taker Buy Base Asset Volume",
                    "Taker Buy Quote Asset Volume",
                    "Ignore",
                ],
            )

            # Convert timestamp to datetime
            df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
            df["Close Time"] = pd.to_datetime(df["Close Time"], unit="ms")

            # Set 'Open Time' as index
            df.set_index("Open Time", inplace=True)

            # Select and rename columns to be consistent
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df = df.astype(float)

            return df

        except Exception as e:
            print(f"Error fetching data from Binance for {symbol}: {e}")
            return pd.DataFrame()

    def get_stock_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Binance does not provide stock data.
        """
        print("Binance does not provide stock data.")
        return pd.DataFrame()
