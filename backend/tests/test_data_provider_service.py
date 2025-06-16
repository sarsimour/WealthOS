import pytest
from app.services.data_provider_service import DataProviderService
import pandas as pd
from datetime import datetime, timedelta
import requests


def is_binance_blocked():
    """Checks if the Binance API is accessible."""
    try:
        response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
        # Status code 451 is used by Binance for geo-restrictions.
        if response.status_code == 451:
            print("Binance API is blocked by location, skipping test.")
            return True
    except requests.exceptions.RequestException:
        # If we can't connect, don't skip; let the test fail to see the network error.
        return False
    return False


@pytest.fixture
def data_provider_service():
    return DataProviderService()


def test_get_chinese_stock_data(data_provider_service):
    """
    Test fetching Chinese stock data (e.g., Ping An Bank of China).
    Symbol: 000001
    """
    symbol = "000001"
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

    df = data_provider_service.get_data(symbol, start_date, end_date, market="cn")

    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    assert "开盘" in df.columns  # Akshare uses Chinese columns


def test_get_us_stock_data(data_provider_service):
    """
    Test fetching US stock data (e.g., Apple).
    """
    symbol = "AAPL"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    df = data_provider_service.get_data(symbol, start_date, end_date, market="us")

    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    assert "Open" in df.columns


def test_get_crypto_data_yfinance(data_provider_service):
    """
    Test fetching crypto data from Yahoo Finance (e.g., BTC-USD).
    """
    symbol = "BTC-USD"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    df = data_provider_service.get_data(
        symbol, start_date, end_date, asset_type="crypto"
    )

    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    assert "Open" in df.columns


@pytest.mark.skipif(
    is_binance_blocked(), reason="Binance API is blocked in this location."
)
def test_get_crypto_data_binance(data_provider_service):
    """
    Test fetching crypto data from Binance (e.g., BTCUSDT).
    """
    symbol = "BTCUSDT"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    df = data_provider_service.get_data(
        symbol, start_date, end_date, market="binance", asset_type="crypto"
    )

    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    assert "Open" in df.columns
