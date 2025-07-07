"""
Comprehensive test script for fund_data.py - outputs results to Excel files for review.

This script tests all functions in the fund_data module and saves the results
to Excel files for easy inspection and validation.
"""

import asyncio
import logging
import sys
import os
import time
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

from app.data.code_mapping import add_exchange_suffix, is_fund_code

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Output directory for Excel files
OUTPUT_DIR = Path("test_results")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_to_excel(df: pd.DataFrame, filename: str, sheet_name: str = "Sheet1"):
    """Save DataFrame to Excel file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"{timestamp}_{filename}.xlsx"

    try:
        df.to_excel(output_file, sheet_name=sheet_name, index=False)
        print(f"💾 Saved to: {output_file}")
        return str(output_file)
    except Exception as e:
        print(f"❌ Failed to save Excel file: {e}")
        return None


def print_summary_table(df: pd.DataFrame, title: str):
    """Print a nice summary table."""
    print(f"\n📊 {title}")
    print("-" * 60)
    print(f"Total rows: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")

    if not df.empty:
        print("\nFirst 3 rows:")
        print(df.head(3).to_string(index=False, max_cols=5))


async def test_fund_list():
    """Test getting fund list and verify .OF suffix functionality."""
    print("\n" + "=" * 60)
    print("🔄 Testing: get_fund_list() and .OF suffix functionality")
    print("=" * 60)

    try:
        # Test getting fund list
        print("Fetching fund list from AKShare...")
        start_time = time.time()
        funds_df = await get_fund_list(use_cache=False)  # Force fresh data
        fetch_time = time.time() - start_time

        print(f"✅ Successfully fetched {len(funds_df):,} funds in {fetch_time:.2f}s")
        print_summary_table(funds_df, "Fund List Data")

        # Test .OF suffix functionality
        print("\n🔍 Testing .OF suffix functionality:")
        sample_codes = funds_df["基金代码"].head(10).tolist()

        suffix_results = []
        for code in sample_codes:
            is_fund = is_fund_code(code)
            with_suffix = add_exchange_suffix(code)
            suffix_results.append(
                {
                    "原始代码": code,
                    "识别为基金": is_fund,
                    "带后缀代码": with_suffix,
                    "后缀正确": with_suffix.endswith(".OF"),
                }
            )

        suffix_df = pd.DataFrame(suffix_results)
        print_summary_table(suffix_df, "Fund Code Suffix Test")

        # Verify all funds get .OF suffix
        correct_suffix_count = suffix_df["后缀正确"].sum()
        print(
            f"\n✅ Suffix test: {correct_suffix_count}/{len(suffix_df)} funds correctly got .OF suffix"
        )

        # Save results
        save_to_excel(funds_df, "01_fund_list", "All_Funds")
        save_to_excel(suffix_df, "01_suffix_test", "Suffix_Test")

        # Save a sample for further testing
        sample_funds = funds_df.head(50)
        save_to_excel(sample_funds, "01_fund_sample", "Sample_Funds")

        return funds_df, sample_funds

    except Exception as e:
        print(f"❌ Failed to get fund list: {e}")
        return None, None


async def test_fund_basic_info(test_symbols: list):
    """Test getting fund basic information."""
    print("\n" + "=" * 60)
    print("🔄 Testing: get_fund_basic_info()")
    print("=" * 60)

    basic_info_results = []

    for symbol in test_symbols[:10]:  # Test first 10 funds
        try:
            print(f"\nTesting basic info for: {symbol}")
            start_time = time.time()
            basic_info = await get_fund_basic_info(symbol, use_cache=False)
            fetch_time = time.time() - start_time

            # Convert to DataFrame row
            info_row = basic_info.copy()
            info_row["测试代码"] = symbol
            info_row["获取时间秒"] = round(fetch_time, 2)
            basic_info_results.append(info_row)

            print(f"✅ Got basic info for {symbol} in {fetch_time:.2f}s")
            print(f"   基金名称: {basic_info.get('基金简称', 'N/A')}")
            print(f"   带后缀代码: {basic_info.get('基金代码_带后缀', 'N/A')}")

        except Exception as e:
            print(f"❌ Failed to get basic info for {symbol}: {e}")
            basic_info_results.append(
                {"测试代码": symbol, "错误信息": str(e), "获取时间秒": 0}
            )

    # Create DataFrame and save
    if basic_info_results:
        basic_info_df = pd.DataFrame(basic_info_results)
        print_summary_table(basic_info_df, "Fund Basic Info Results")
        save_to_excel(basic_info_df, "02_basic_info", "Basic_Info")

    return basic_info_results


async def test_fund_nav_history(test_symbols: list):
    """Test getting fund NAV history."""
    print("\n" + "=" * 60)
    print("🔄 Testing: get_fund_nav_history()")
    print("=" * 60)

    nav_results = {}
    nav_summaries = []

    # Test date range (last 30 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    for symbol in test_symbols[:5]:  # Test first 5 funds
        try:
            print(f"\nTesting NAV history for: {symbol}")
            print(f"Date range: {start_date} to {end_date}")

            start_time = time.time()
            nav_df = await get_fund_nav_history(
                symbol, start_date=start_date, end_date=end_date, use_cache=False
            )
            fetch_time = time.time() - start_time

            print(f"✅ Got {len(nav_df)} NAV records for {symbol} in {fetch_time:.2f}s")

            if not nav_df.empty:
                print(
                    f"   Date range: {nav_df['净值日期'].min()} to {nav_df['净值日期'].max()}"
                )
                print(f"   Latest NAV: {nav_df.iloc[-1].get('单位净值', 'N/A')}")

            # Add symbol for identification
            nav_df["基金代码"] = symbol
            nav_results[symbol] = nav_df

            # Create summary
            nav_summaries.append(
                {
                    "基金代码": symbol,
                    "记录数": len(nav_df),
                    "获取时间秒": round(fetch_time, 2),
                    "开始日期": nav_df["净值日期"].min() if not nav_df.empty else None,
                    "结束日期": nav_df["净值日期"].max() if not nav_df.empty else None,
                    "最新净值": (
                        nav_df.iloc[-1].get("单位净值", None)
                        if not nav_df.empty
                        else None
                    ),
                }
            )

            # Save individual NAV history
            save_to_excel(nav_df, f"03_nav_{symbol}", "NAV_History")

        except Exception as e:
            print(f"❌ Failed to get NAV history for {symbol}: {e}")
            nav_summaries.append(
                {"基金代码": symbol, "错误信息": str(e), "获取时间秒": 0}
            )

    # Save summary
    if nav_summaries:
        nav_summary_df = pd.DataFrame(nav_summaries)
        print_summary_table(nav_summary_df, "NAV History Summary")
        save_to_excel(nav_summary_df, "03_nav_summary", "NAV_Summary")

    # Combine all NAV data
    if nav_results:
        all_nav_df = pd.concat(nav_results.values(), ignore_index=True)
        save_to_excel(all_nav_df, "03_nav_combined", "All_NAV_Data")

    return nav_results


async def test_fund_holdings(test_symbols: list):
    """Test getting fund holdings."""
    print("\n" + "=" * 60)
    print("🔄 Testing: get_fund_holdings()")
    print("=" * 60)

    holdings_results = {}
    holdings_summaries = []

    for symbol in test_symbols[:5]:  # Test first 5 funds
        try:
            print(f"\nTesting holdings for: {symbol}")
            start_time = time.time()
            holdings_df = await get_fund_holdings(symbol, use_cache=False)
            fetch_time = time.time() - start_time

            print(
                f"✅ Got {len(holdings_df)} holdings for {symbol} in {fetch_time:.2f}s"
            )

            if not holdings_df.empty:
                print(f"   Columns: {', '.join(holdings_df.columns[:3])}...")
                if "股票代码_带后缀" in holdings_df.columns:
                    suffix_count = (
                        holdings_df["股票代码_带后缀"]
                        .str.contains(r"\.(SH|SZ|BJ)$")
                        .sum()
                    )
                    print(
                        f"   Stock codes with suffix: {suffix_count}/{len(holdings_df)}"
                    )

                print("   Top 3 holdings:")
                print(
                    holdings_df.head(3)[
                        ["股票代码", "股票简称", "占净值比例"]
                    ].to_string(index=False)
                    if all(
                        col in holdings_df.columns
                        for col in ["股票代码", "股票简称", "占净值比例"]
                    )
                    else holdings_df.head(3).to_string(index=False)
                )

            # Add fund symbol for identification
            holdings_df["基金代码"] = symbol
            holdings_results[symbol] = holdings_df

            # Create summary
            holdings_summaries.append(
                {
                    "基金代码": symbol,
                    "持仓数量": len(holdings_df),
                    "获取时间秒": round(fetch_time, 2),
                    "包含股票代码": "股票代码" in holdings_df.columns,
                    "包含带后缀代码": "股票代码_带后缀" in holdings_df.columns,
                    "数据列数": len(holdings_df.columns),
                }
            )

            # Save individual fund holdings
            save_to_excel(holdings_df, f"04_holdings_{symbol}", "Holdings")

        except Exception as e:
            print(f"❌ Failed to get holdings for {symbol}: {e}")
            holdings_summaries.append(
                {"基金代码": symbol, "错误信息": str(e), "获取时间秒": 0}
            )

    # Save summary
    if holdings_summaries:
        holdings_summary_df = pd.DataFrame(holdings_summaries)
        print_summary_table(holdings_summary_df, "Holdings Summary")
        save_to_excel(holdings_summary_df, "04_holdings_summary", "Holdings_Summary")

    # Combine all holdings data
    if holdings_results:
        all_holdings_df = pd.concat(holdings_results.values(), ignore_index=True)
        save_to_excel(all_holdings_df, "04_holdings_combined", "All_Holdings")

    return holdings_results


async def test_stock_codes_extraction(holdings_results: dict):
    """Test extracting all stock codes from holdings."""
    print("\n" + "=" * 60)
    print("🔄 Testing: get_all_stock_codes_from_holdings()")
    print("=" * 60)

    if not holdings_results:
        print("❌ No holdings data available for stock code extraction")
        return None

    try:
        test_symbols = list(holdings_results.keys())
        print(f"Extracting stock codes from {len(test_symbols)} funds...")

        start_time = time.time()
        all_stock_codes = await get_all_stock_codes_from_holdings(
            test_symbols, use_cache=True
        )
        extract_time = time.time() - start_time

        print(
            f"✅ Extracted {len(all_stock_codes)} unique stock codes in {extract_time:.2f}s"
        )

        # Analyze suffix distribution
        suffix_analysis = {}
        for code in all_stock_codes:
            if "." in code:
                suffix = code.split(".")[-1]
                suffix_analysis[suffix] = suffix_analysis.get(suffix, 0) + 1
            else:
                suffix_analysis["NO_SUFFIX"] = suffix_analysis.get("NO_SUFFIX", 0) + 1

        print("\n📊 Stock code suffix distribution:")
        for suffix, count in sorted(suffix_analysis.items()):
            print(f"   .{suffix}: {count:,} codes")

        # Create DataFrame for analysis
        stock_codes_df = pd.DataFrame(
            {
                "股票代码": all_stock_codes,
                "交易所": [
                    code.split(".")[-1] if "." in code else "UNKNOWN"
                    for code in all_stock_codes
                ],
            }
        )

        print_summary_table(stock_codes_df, "Extracted Stock Codes")
        save_to_excel(stock_codes_df, "05_stock_codes", "Stock_Codes")

        return all_stock_codes

    except Exception as e:
        print(f"❌ Failed to extract stock codes: {e}")
        return None


async def test_cache_performance(test_symbols: list):
    """Test cache performance by comparing cached vs uncached calls."""
    print("\n" + "=" * 60)
    print("🔄 Testing: Cache Performance")
    print("=" * 60)

    if not test_symbols:
        print("❌ No test symbols available for cache testing")
        return

    test_symbol = test_symbols[0]
    print(f"Testing cache performance with fund: {test_symbol}")

    # Clear cache first
    cleared_files = clear_cache()
    print(f"🗑️ Cleared {cleared_files} cache files")

    performance_results = []

    # Test 1: First call (no cache)
    print("\n1️⃣ First call (no cache):")
    start_time = time.time()
    try:
        result1 = await get_fund_basic_info(test_symbol, use_cache=True)
        time1 = time.time() - start_time
        print(f"   Time: {time1:.2f}s")
        performance_results.append(
            {"测试": "首次调用(无缓存)", "时间秒": round(time1, 3), "成功": True}
        )
    except Exception as e:
        time1 = time.time() - start_time
        print(f"   Failed: {e}")
        performance_results.append(
            {
                "测试": "首次调用(无缓存)",
                "时间秒": round(time1, 3),
                "成功": False,
                "错误": str(e),
            }
        )

    # Test 2: Second call (with cache)
    print("\n2️⃣ Second call (with cache):")
    start_time = time.time()
    try:
        result2 = await get_fund_basic_info(test_symbol, use_cache=True)
        time2 = time.time() - start_time
        print(f"   Time: {time2:.2f}s")

        if time1 > 0:
            speedup = time1 / time2 if time2 > 0 else float("inf")
            print(f"   Speedup: {speedup:.1f}x faster")

        performance_results.append(
            {
                "测试": "第二次调用(有缓存)",
                "时间秒": round(time2, 3),
                "成功": True,
                "加速倍数": round(speedup, 1) if time1 > 0 and time2 > 0 else None,
            }
        )
    except Exception as e:
        time2 = time.time() - start_time
        print(f"   Failed: {e}")
        performance_results.append(
            {
                "测试": "第二次调用(有缓存)",
                "时间秒": round(time2, 3),
                "成功": False,
                "错误": str(e),
            }
        )

    # Test 3: Multiple cached calls
    print("\n3️⃣ Multiple cached calls:")
    cached_times = []
    for i in range(5):
        start_time = time.time()
        try:
            await get_fund_basic_info(test_symbol, use_cache=True)
            cached_times.append(time.time() - start_time)
        except:
            break

    if cached_times:
        avg_cached_time = sum(cached_times) / len(cached_times)
        print(f"   Average time for {len(cached_times)} calls: {avg_cached_time:.3f}s")
        performance_results.append(
            {
                "测试": f"多次缓存调用(平均)",
                "时间秒": round(avg_cached_time, 3),
                "成功": True,
                "调用次数": len(cached_times),
            }
        )

    # Save performance results
    if performance_results:
        performance_df = pd.DataFrame(performance_results)
        print_summary_table(performance_df, "Cache Performance Results")
        save_to_excel(performance_df, "06_cache_performance", "Performance")

    return performance_results


async def main():
    """Main test function."""
    print("🚀 Starting Comprehensive Fund Data System Test")
    print("=" * 80)

    # Test 1: Fund list and suffix functionality
    funds_df, sample_funds = await test_fund_list()
    if funds_df is None:
        print("❌ Fund list test failed. Stopping tests.")
        return

    # Get test symbols from sample
    test_symbols = (
        sample_funds["基金代码"].head(10).tolist()
        if sample_funds is not None
        else ["000001", "000002", "000003"]
    )
    print(f"\n🎯 Using test symbols: {test_symbols}")

    # Test 2: Fund basic info
    basic_info_results = await test_fund_basic_info(test_symbols)

    # Test 3: Fund NAV history
    nav_results = await test_fund_nav_history(test_symbols)

    # Test 4: Fund holdings
    holdings_results = await test_fund_holdings(test_symbols)

    # Test 5: Stock codes extraction
    stock_codes = await test_stock_codes_extraction(holdings_results)

    # Test 6: Cache performance
    performance_results = await test_cache_performance(test_symbols)

    # Final summary
    print("\n" + "=" * 80)
    print("🎉 TEST SUMMARY")
    print("=" * 80)
    print(f"📊 Total funds found: {len(funds_df):,}")
    print(f"🧪 Test symbols used: {len(test_symbols)}")
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # List generated Excel files
    excel_files = list(OUTPUT_DIR.glob("*.xlsx"))
    print(f"\n📋 Generated {len(excel_files)} Excel files:")
    for file in sorted(excel_files):
        file_size = file.stat().st_size / 1024  # KB
        print(f"   📄 {file.name} ({file_size:.1f} KB)")

    print(
        "\n✅ All tests completed! Check the Excel files in the test_results directory."
    )


if __name__ == "__main__":
    # Set up event loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
