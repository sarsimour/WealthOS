import pandas as pd
import yfinance as yf


class YFinanceProvider:
    def get_stock_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Get stock data from Yahoo Finance.
        """
        try:
            stock = yf.Ticker(symbol)
            stock_data = stock.history(start=start_date, end=end_date)
            return stock_data
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
            return pd.DataFrame()

    def get_crypto_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Get crypto data from Yahoo Finance.
        """
        try:
            crypto = yf.Ticker(symbol)
            crypto_data = crypto.history(start=start_date, end=end_date)
            return crypto_data
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
            return pd.DataFrame()
