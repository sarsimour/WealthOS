#!/usr/bin/env python3
"""
Test script for the Fund of Funds (FOF) analysis system.

This script tests the complete workflow:
1. Code mapping and name normalization
2. Mock Barra factor generation
3. Portfolio factor calculation
4. Relative risk and performance analysis
"""

import sys
import asyncio
from pathlib import Path
import pytest

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Please install: pip install pandas numpy")
    sys.exit(1)

# Import our modules
from app.data.code_mapping import add_exchange_suffix, batch_add_suffix
from app.data.name_mapping import (
    normalize_alipay_fund_name,
    normalize_akshare_fund_name,
)
from app.data.barra_factors import get_barra_factors, generate_mock_barra_factors
from app.analysis.fof.portfolio_analysis import (
    calculate_portfolio_barra_factors,
    create_benchmark_from_funds,
    calculate_relative_risk_exposure,
    calculate_relative_performance_metrics,
)


def test_code_mapping():
    """Test code mapping functionality."""
    print("=" * 60)
    print("TESTING CODE MAPPING")
    print("=" * 60)

    test_codes = [
        "000001",  # SZSE main board
        "600000",  # SSE A share
        "300001",  # SZSE ChiNext
        "510050",  # SSE ETF
        "159915",  # SZSE ETF
        "920001",  # BSE stock
    ]

    print("\nCode suffix mapping:")
    for code in test_codes:
        result = add_exchange_suffix(code)
        print(f"  {code} -> {result}")

    print("\nBatch processing:")
    batch_results = batch_add_suffix(test_codes)
    for original, with_suffix in batch_results.items():
        print(f"  {original} -> {with_suffix}")

        # Add assertions for proper pytest behavior
    assert len(test_codes) == 6
    assert add_exchange_suffix("000001") == "000001.SZ"
    assert add_exchange_suffix("600000") == "600000.SH"


def test_name_mapping():
    """Test fund name mapping functionality."""
    print("\n" + "=" * 60)
    print("TESTING NAME MAPPING")
    print("=" * 60)

    test_alipay_names = [
        "华夏成长混合(A类)",
        "易方达蓝筹精选混合（A）",
        "南方积极配置混合",
        "嘉实沪深300ETF联接(A)",
    ]

    test_akshare_names = [
        "华夏成长证券投资基金",
        "易方达蓝筹精选混合型证券投资基金",
        "南方积极配置混合型证券投资基金",
        "嘉实沪深300交易型开放式指数证券投资基金联接基金",
    ]

    print("\nAlipay name normalization:")
    for name in test_alipay_names:
        normalized = normalize_alipay_fund_name(name)
        print(f"  '{name}' -> '{normalized}'")

    print("\nAKShare name normalization:")
    for name in test_akshare_names:
        normalized = normalize_akshare_fund_name(name)
        print(f"  '{name}' -> '{normalized}'")

    # Add assertions for proper pytest behavior
    assert normalize_alipay_fund_name("华夏成长混合(A类)") == "华夏成长混合"
    assert normalize_akshare_fund_name("华夏成长证券投资基金") == "华夏成长"


@pytest.fixture
def stock_codes():
    """Fixture providing test stock codes."""
    return ["000001", "600000", "300001", "510050", "159915", "920001"]


@pytest.fixture
def barra_factors(stock_codes):
    """Test Barra factor generation."""
    print("\n" + "=" * 60)
    print("TESTING BARRA FACTORS")
    print("=" * 60)

    print(f"\nGenerating mock Barra factors for {len(stock_codes)} stocks...")

    # Add suffixes to stock codes
    stock_codes_with_suffix = [add_exchange_suffix(code) for code in stock_codes]

    # Generate mock factors synchronously for pytest
    from app.data.barra_factors import generate_mock_barra_factors

    barra_factors = generate_mock_barra_factors(stock_codes_with_suffix)

    print(f"Factor data shape: {barra_factors.shape}")
    print(f"Available factors: {list(barra_factors.columns)}")
    print("\nSample factor data:")
    print(barra_factors.head())

    return barra_factors


async def test_barra_factors_async(stock_codes):
    """Test Barra factor generation."""
    print("\n" + "=" * 60)
    print("TESTING BARRA FACTORS")
    print("=" * 60)

    print(f"\nGenerating mock Barra factors for {len(stock_codes)} stocks...")

    # Add suffixes to stock codes
    stock_codes_with_suffix = [add_exchange_suffix(code) for code in stock_codes]

    # Generate mock factors
    barra_factors = await get_barra_factors(stock_codes_with_suffix, force_mock=True)

    print(f"Factor data shape: {barra_factors.shape}")
    print(f"Available factors: {list(barra_factors.columns)}")
    print("\nSample factor data:")
    print(barra_factors.head())

    # Add assertions for proper pytest behavior
    assert barra_factors.shape[0] == len(stock_codes)
    assert "SIZE" in barra_factors.columns
    assert "BETA" in barra_factors.columns

    return barra_factors


def test_portfolio_analysis(barra_factors):
    """Test portfolio analysis functionality."""
    print("\n" + "=" * 60)
    print("TESTING PORTFOLIO ANALYSIS")
    print("=" * 60)

    # Create mock fund holdings
    stock_codes = list(barra_factors.index)

    # Fund 1 holdings
    fund1_holdings = pd.DataFrame(
        {
            "股票代码_带后缀": stock_codes[:3],
            "占净值比例": [0.4, 0.35, 0.25],
            "股票名称": ["Stock A", "Stock B", "Stock C"],
            "fund_code": ["fund1", "fund1", "fund1"],
        }
    )

    # Fund 2 holdings (different weights)
    fund2_holdings = pd.DataFrame(
        {
            "股票代码_带后缀": stock_codes[1:4],
            "占净值比例": [0.3, 0.4, 0.3],
            "股票名称": ["Stock B", "Stock C", "Stock D"],
            "fund_code": ["fund2", "fund2", "fund2"],
        }
    )

    print(f"\nFund 1 holdings:")
    print(fund1_holdings)
    print(f"\nFund 2 holdings:")
    print(fund2_holdings)

    # Calculate portfolio factors for both funds
    print("\n1. Calculating portfolio Barra factors...")

    fund1_factors = calculate_portfolio_barra_factors(fund1_holdings, barra_factors)
    fund2_factors = calculate_portfolio_barra_factors(fund2_holdings, barra_factors)

    print(f"\nFund 1 factors:")
    print(fund1_factors.round(4))
    print(f"\nFund 2 factors:")
    print(fund2_factors.round(4))

    # Create composite benchmark
    print("\n2. Creating composite benchmark...")
    benchmark_holdings = create_benchmark_from_funds(
        [fund1_holdings, fund2_holdings]  # Equal weighting - average of both funds
    )

    print(f"Benchmark holdings (average of both funds):")
    print(benchmark_holdings)
    print(f"Total benchmark weight: {benchmark_holdings['占净值比例'].sum():.4f}")
    print("Note: Total weight < 1.0 reflects average stock exposure across funds")

    benchmark_factors = calculate_portfolio_barra_factors(
        benchmark_holdings, barra_factors, stock_code_col="股票代码_带后缀"
    )

    print(f"\nBenchmark factors:")
    print(benchmark_factors.round(4))

    # Calculate relative risk exposure
    print("\n3. Calculating relative risk exposure...")

    fund1_relative = calculate_relative_risk_exposure(fund1_factors, benchmark_factors)
    fund2_relative = calculate_relative_risk_exposure(fund2_factors, benchmark_factors)

    print(f"\nFund 1 vs Benchmark relative exposure:")
    print(fund1_relative.round(4))
    print(f"\nFund 2 vs Benchmark relative exposure:")
    print(fund2_relative.round(4))

    # Add assertions for proper pytest behavior
    assert fund1_factors is not None
    assert fund2_factors is not None
    assert benchmark_factors is not None
    assert fund1_factors.shape[0] > 0
    assert fund2_factors.shape[0] > 0
    assert benchmark_factors.shape[0] > 0


def test_performance_analysis():
    """Test performance analysis functionality."""
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE ANALYSIS")
    print("=" * 60)

    # Generate mock return data
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=252, freq="D")  # 1 year of daily data

    # Portfolio returns (slightly outperforming)
    portfolio_returns = pd.Series(
        np.random.normal(0.0008, 0.02, 252),  # 0.08% daily mean, 2% volatility
        index=dates,
        name="portfolio",
    )

    # Benchmark returns
    benchmark_returns = pd.Series(
        np.random.normal(0.0005, 0.018, 252),  # 0.05% daily mean, 1.8% volatility
        index=dates,
        name="benchmark",
    )

    print(f"\nGenerated {len(portfolio_returns)} days of return data")
    print(
        f"Portfolio: mean={portfolio_returns.mean():.4f}, std={portfolio_returns.std():.4f}"
    )
    print(
        f"Benchmark: mean={benchmark_returns.mean():.4f}, std={benchmark_returns.std():.4f}"
    )

    # Calculate performance metrics
    print("\nCalculating performance metrics...")
    performance_metrics = calculate_relative_performance_metrics(
        portfolio_returns,
        benchmark_returns,
        risk_free_rate=0.02,  # 2% annual risk-free rate
    )

    print("\nPerformance Metrics:")
    print("-" * 40)
    for metric, value in performance_metrics.items():
        if isinstance(value, (int, float)):
            print(f"{metric:25s}: {value:8.4f}")
        else:
            print(f"{metric:25s}: {value}")

    # Add assertions for proper pytest behavior
    assert performance_metrics is not None
    assert "portfolio_total_return" in performance_metrics
    assert "benchmark_total_return" in performance_metrics
    assert "tracking_error" in performance_metrics


def create_summary_report(
    fund1_factors, fund2_factors, benchmark_factors, performance_metrics
):
    """Create a summary report of the analysis."""
    print("\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60)

    print("\n1. FACTOR EXPOSURE SUMMARY")
    print("-" * 30)

    # Key factors to highlight
    key_factors = ["SIZE", "BETA", "BTOP", "GROWTH"]

    summary_df = pd.DataFrame(
        {
            "Fund_1": fund1_factors[key_factors],
            "Fund_2": fund2_factors[key_factors],
            "Benchmark": benchmark_factors[key_factors],
        }
    )

    summary_df["Fund1_vs_Bench"] = summary_df["Fund_1"] - summary_df["Benchmark"]
    summary_df["Fund2_vs_Bench"] = summary_df["Fund_2"] - summary_df["Benchmark"]

    print(summary_df.round(4))

    print("\n2. PERFORMANCE SUMMARY")
    print("-" * 30)

    key_metrics = [
        "portfolio_total_return",
        "benchmark_total_return",
        "excess_return",
        "tracking_error",
        "information_ratio",
        "beta",
        "alpha",
    ]

    for metric in key_metrics:
        if metric in performance_metrics:
            value = performance_metrics[metric]
            print(f"{metric:25s}: {value:8.4f}")

    print("\n3. RISK ANALYSIS")
    print("-" * 30)

    # Analyze factor exposures
    fund1_risk = abs(summary_df["Fund1_vs_Bench"]).sum()
    fund2_risk = abs(summary_df["Fund2_vs_Bench"]).sum()

    print(f"Fund 1 total factor risk:    {fund1_risk:.4f}")
    print(f"Fund 2 total factor risk:    {fund2_risk:.4f}")
    print(
        f"Tracking error:              {performance_metrics.get('tracking_error', 0):.4f}"
    )
    print(
        f"Correlation with benchmark:  {performance_metrics.get('correlation', 0):.4f}"
    )

    print("\n4. RECOMMENDATIONS")
    print("-" * 30)

    if performance_metrics.get("information_ratio", 0) > 0.5:
        print("✓ Good risk-adjusted performance (IR > 0.5)")
    else:
        print("⚠ Consider improving risk-adjusted returns")

    if performance_metrics.get("tracking_error", 0) < 0.05:
        print("✓ Low tracking error - good benchmark alignment")
    else:
        print("⚠ High tracking error - consider risk management")

    if fund1_risk < fund2_risk:
        print("✓ Fund 1 has lower factor risk vs benchmark")
    else:
        print("✓ Fund 2 has lower factor risk vs benchmark")


async def main():
    """Run all tests."""
    print("FOF ANALYSIS SYSTEM TEST")
    print("=" * 60)
    print("Testing the complete Fund of Funds analysis workflow...")

    try:
        # Test 1: Code mapping
        test_code_mapping()

        # Define test codes for the remaining tests
        test_codes = ["000001", "600000", "300001", "510050", "159915", "920001"]

        # Test 2: Name mapping
        test_name_mapping()

        # Test 3: Barra factors
        barra_factors = await test_barra_factors_async(test_codes)

        # Test 4: Portfolio analysis
        test_portfolio_analysis(barra_factors)

        # Test 5: Performance analysis
        test_performance_analysis()

        print("\n" + "=" * 60)
        print("PORTFOLIO ANALYSIS TESTS COMPLETED")
        print("=" * 60)

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 60)
        print("\nThe FOF analysis system is working correctly.")
        print("You can now:")
        print("1. Replace mock Barra factors with real Excel data")
        print("2. Integrate with AKShare for real fund data")
        print("3. Add caching with Redis or similar")
        print("4. Implement Polars for faster computation")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
