import akshare as ak
import pandas as pd


class AkshareProvider:
    def get_stock_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Get stock data from Akshare.
        """
        try:
            stock_data = ak.stock_zh_a_hist(
                symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq"
            )
            return stock_data
        except Exception as e:
            print(f"Error fetching data from Akshare for {symbol}: {e}")
            return pd.DataFrame()

    def get_crypto_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Akshare does not directly support crypto, returning empty dataframe.
        """
        print("Akshare does not provide cryptocurrency data.")
        return pd.DataFrame()
