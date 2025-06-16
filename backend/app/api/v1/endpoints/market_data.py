from fastapi import APIRouter, Query
from app.services.data_provider_service import DataProviderService
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()
data_provider_service = DataProviderService()


@router.get("/historical")
def get_historical_data(
    symbol: str,
    market: str = "other",
    asset_type: str = "stock",
    end_date: str = Query(None),
    start_date: str = Query(None),
):
    """
    Fetches historical market data for a given symbol.
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    # The data provider service expects akshare dates to be in 'YYYYMMDD' format
    akshare_start_date = start_date.replace("-", "")
    akshare_end_date = end_date.replace("-", "")

    if market == "cn":
        df = data_provider_service.get_data(
            symbol,
            akshare_start_date,
            akshare_end_date,
            market=market,
            asset_type=asset_type,
        )
    else:
        df = data_provider_service.get_data(
            symbol, start_date, end_date, market=market, asset_type=asset_type
        )

    if df.empty:
        return {"error": "Could not retrieve data."}

    # Reset index to make date a column
    df = df.reset_index()

    # Rename columns for consistency if needed
    if market == "cn":
        df = df.rename(
            columns={
                "日期": "Date",
                "开盘": "Open",
                "收盘": "Close",
                "最高": "High",
                "最低": "Low",
                "成交量": "Volume",
            }
        )
        # Convert date to string
        df["Date"] = df["Date"].astype(str)
    else:
        # For yfinance, the date is already the index, and becomes 'Date' or 'Open Time' after reset_index
        if "Open Time" in df.columns:  # from binance
            df = df.rename(columns={"Open Time": "Date"})
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    return df.to_dict(orient="records")
