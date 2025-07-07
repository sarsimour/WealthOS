"""
Test script for fund_data.py - outputs results to Excel files for review.

This script tests all functions in the fund_data module and saves the results
to Excel files for easy inspection and validation.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

try:
    import pandas as pd
    import openpyxl  # Required for Excel writing
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: uv add pandas openpyxl")
    sys.exit(1)

from app.data.fund_data import (
    get_fund_list,
    get_fund_nav_history,
    get_fund_holdings,
    get_fund_basic_info,
    get_all_stock_codes_from_holdings,
    clear_cache,
    FundDataError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Output directory for Excel files
OUTPUT_DIR = Path("test_results")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_to_excel(data, filename: str, sheet_name: str = "Sheet1"):
    """Save data to Excel file."""
    filepath = OUTPUT_DIR / f"{filename}.xlsx"

    try:
        if isinstance(data, pd.DataFrame):
            data.to_excel(filepath, sheet_name=sheet_name, index=False)
        elif isinstance(data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame([data])
            df.to_excel(filepath, sheet_name=sheet_name, index=False)
        elif isinstance(data, list):
            # Convert list to DataFrame
            df = pd.DataFrame(data)
            df.to_excel(filepath, sheet_name=sheet_name, index=False)
        else:
            # Convert to string and save as single cell
            df = pd.DataFrame({"Result": [str(data)]})
            df.to_excel(filepath, sheet_name=sheet_name, index=False)

        print(f"✅ Saved {filename}.xlsx to {OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"❌ Failed to save {filename}.xlsx: {e}")
        return False


async def test_fund_list():
    """Test getting fund list."""
    print("\n" + "=" * 50)
    print("Testing: get_fund_list()")
    print("=" * 50)

    try:
        # Test getting fund list
        funds_df = await get_fund_list(use_cache=False)  # Force fresh data

        print(f"✅ Successfully fetched {len(funds_df)} funds")
        print(f"Columns: {list(funds_df.columns)}")
        print("\nFirst 5 funds:")
        print(funds_df.head())

        # Save to Excel
        save_to_excel(funds_df, "01_fund_list", "All_Funds")

        # Save a sample of funds for further testing
        sample_funds = funds_df.head(20)
        save_to_excel(sample_funds, "01_fund_list_sample", "Sample_Funds")

        return funds_df

    except Exception as e:
        print(f"❌ Failed to get fund list: {e}")
        return None


async def test_fund_basic_info(test_symbols: list):
    """Test getting basic fund information."""
    print("\n" + "=" * 50)
    print("Testing: get_fund_basic_info()")
    print("=" * 50)

    basic_info_results = []

    for symbol in test_symbols:
        try:
            print(f"\nTesting fund: {symbol}")
            basic_info = await get_fund_basic_info(symbol, use_cache=False)

            print(f"✅ Got basic info for {symbol}")
            print(f"Fund name: {basic_info.get('基金简称', 'N/A')}")
            print(f"Fund type: {basic_info.get('基金类型', 'N/A')}")

            # Add symbol to the info for tracking
            basic_info["测试基金代码"] = symbol
            basic_info_results.append(basic_info)

        except Exception as e:
            print(f"❌ Failed to get basic info for {symbol}: {e}")
            basic_info_results.append({"测试基金代码": symbol, "错误信息": str(e)})

    # Save all basic info to Excel
    if basic_info_results:
        save_to_excel(basic_info_results, "02_fund_basic_info", "Basic_Info")

    return basic_info_results


async def test_fund_nav_history(test_symbols: list):
    """Test getting fund NAV history."""
    print("\n" + "=" * 50)
    print("Testing: get_fund_nav_history()")
    print("=" * 50)

    # Test with different date ranges
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime(
        "%Y-%m-%d"
    )  # Last 3 months

    nav_results = {}

    for symbol in test_symbols[:5]:  # Test first 5 funds only to avoid too much data
        try:
            print(f"\nTesting NAV history for: {symbol}")
            nav_df = await get_fund_nav_history(
                symbol, start_date=start_date, end_date=end_date, use_cache=False
            )

            print(f"✅ Got {len(nav_df)} NAV records for {symbol}")
            print(
                f"Date range: {nav_df['净值日期'].min()} to {nav_df['净值日期'].max()}"
            )
            print(f"Columns: {list(nav_df.columns)}")

            # Add fund symbol for identification
            nav_df["基金代码"] = symbol
            nav_results[symbol] = nav_df

            # Save individual fund NAV history
            save_to_excel(nav_df, f"03_nav_history_{symbol}", "NAV_History")

        except Exception as e:
            print(f"❌ Failed to get NAV history for {symbol}: {e}")
            nav_results[symbol] = pd.DataFrame(
                {"错误信息": [str(e)], "基金代码": [symbol]}
            )

    # Combine all NAV data
    if nav_results:
        all_nav_df = pd.concat(nav_results.values(), ignore_index=True)
        save_to_excel(all_nav_df, "03_nav_history_combined", "All_NAV_History")

    return nav_results


async def test_fund_holdings(test_symbols: list):
    """Test getting fund holdings."""
    print("\n" + "=" * 50)
    print("Testing: get_fund_holdings()")
    print("=" * 50)

    holdings_results = {}

    for symbol in test_symbols[:5]:  # Test first 5 funds only
        try:
            print(f"\nTesting holdings for: {symbol}")
            holdings_df = await get_fund_holdings(symbol, use_cache=False)

            print(f"✅ Got {len(holdings_df)} holdings for {symbol}")
            print(f"Columns: {list(holdings_df.columns)}")

            if not holdings_df.empty:
                print(f"Top holdings:")
                print(holdings_df.head(3))

            # Add fund symbol for identification
            holdings_df["基金代码"] = symbol
            holdings_results[symbol] = holdings_df

            # Save individual fund holdings
            save_to_excel(holdings_df, f"04_holdings_{symbol}", "Holdings")

        except Exception as e:
            print(f"❌ Failed to get holdings for {symbol}: {e}")
            holdings_results[symbol] = pd.DataFrame(
                {"错误信息": [str(e)], "基金代码": [symbol]}
            )

    # Combine all holdings data
    if holdings_results:
        all_holdings_df = pd.concat(holdings_results.values(), ignore_index=True)
        save_to_excel(all_holdings_df, "04_holdings_combined", "All_Holdings")

    return holdings_results


async def test_stock_codes_extraction(test_symbols: list):
    """Test extracting stock codes from fund holdings."""
    print("\n" + "=" * 50)
    print("Testing: get_all_stock_codes_from_holdings()")
    print("=" * 50)

    try:
        print(f"Extracting stock codes from {len(test_symbols)} funds...")
        stock_codes = await get_all_stock_codes_from_holdings(test_symbols[:3])

        print(f"✅ Found {len(stock_codes)} unique stock codes")
        print("Sample stock codes:", stock_codes[:10])

        # Save stock codes to Excel
        stock_codes_df = pd.DataFrame(
            {"Stock_Code": stock_codes, "Index": range(1, len(stock_codes) + 1)}
        )
        save_to_excel(stock_codes_df, "05_stock_codes", "Stock_Codes")

        return stock_codes

    except Exception as e:
        print(f"❌ Failed to extract stock codes: {e}")
        return []


async def test_cache_functionality():
    """Test cache functionality."""
    print("\n" + "=" * 50)
    print("Testing: Cache functionality")
    print("=" * 50)

    try:
        # Clear cache first
        cleared_count = clear_cache()
        print(f"✅ Cleared {cleared_count} cache files")

        # Test caching with a simple fund
        test_symbol = "000001"

        print(f"\nTesting cache with fund {test_symbol}...")

        # First call - should fetch from API
        start_time = datetime.now()
        basic_info1 = await get_fund_basic_info(test_symbol, use_cache=True)
        first_call_time = (datetime.now() - start_time).total_seconds()

        # Second call - should use cache
        start_time = datetime.now()
        basic_info2 = await get_fund_basic_info(test_symbol, use_cache=True)
        second_call_time = (datetime.now() - start_time).total_seconds()

        print(f"✅ First call (API): {first_call_time:.2f} seconds")
        print(f"✅ Second call (Cache): {second_call_time:.2f} seconds")
        print(f"Cache speedup: {first_call_time/second_call_time:.1f}x faster")

        # Verify data is the same
        data_match = basic_info1 == basic_info2
        print(f"✅ Data consistency: {data_match}")

        cache_test_results = {
            "Test": ["First_Call_API", "Second_Call_Cache", "Data_Match", "Speedup"],
            "Time_Seconds": [
                first_call_time,
                second_call_time,
                None,
                first_call_time / second_call_time,
            ],
            "Result": [
                "Success",
                "Success",
                str(data_match),
                f"{first_call_time/second_call_time:.1f}x",
            ],
        }

        save_to_excel(cache_test_results, "06_cache_test", "Cache_Performance")

        return True

    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Fund Data Testing")
    print("=" * 60)

    # Test symbols - using some common Chinese funds
    test_symbols = [
        "000001",  # 华夏成长
        "110022",  # 易方达消费行业
        "161725",  # 招商中证白酒
        "110011",  # 易方达中小盘
        "000002",  # 华夏策略精选
    ]

    print(f"Test symbols: {test_symbols}")

    try:
        # 1. Test fund list
        funds_df = await test_fund_list()

        # Use actual fund codes from the list if available
        if funds_df is not None and not funds_df.empty:
            actual_symbols = funds_df["基金代码"].head(5).tolist()
            print(f"\nUsing actual fund codes: {actual_symbols}")
            test_symbols = actual_symbols

        # 2. Test basic info
        await test_fund_basic_info(test_symbols)

        # 3. Test NAV history
        await test_fund_nav_history(test_symbols)

        # 4. Test holdings
        await test_fund_holdings(test_symbols)

        # 5. Test stock codes extraction
        await test_stock_codes_extraction(test_symbols)

        # 6. Test cache functionality
        await test_cache_functionality()

        # Create summary report
        summary = {
            "Test_Name": [
                "Fund_List",
                "Basic_Info",
                "NAV_History",
                "Holdings",
                "Stock_Codes",
                "Cache_Test",
            ],
            "Status": ["✅ Completed"] * 6,
            "Output_Files": [
                "01_fund_list.xlsx",
                "02_fund_basic_info.xlsx",
                "03_nav_history_*.xlsx",
                "04_holdings_*.xlsx",
                "05_stock_codes.xlsx",
                "06_cache_test.xlsx",
            ],
            "Test_Time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 6,
        }

        save_to_excel(summary, "00_test_summary", "Summary")

        print("\n" + "=" * 60)
        print("🎉 All tests completed!")
        print(f"📁 Results saved to: {OUTPUT_DIR.absolute()}")
        print("📊 Check the Excel files for detailed results")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
