"""
Fund of Funds (FOF) portfolio analysis utilities.

This module provides functions for:
1. Calculating portfolio Barra factors from holdings
2. Computing relative risk exposure vs benchmarks
3. Analyzing relative performance vs benchmarks
4. Fast computation using optimized data structures
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from datetime import datetime

try:
    import numpy as np
except ImportError:
    np = None

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl
else:
    try:
        import pandas as pd
    except ImportError:
        pd = None

    try:
        import polars as pl
    except ImportError:
        pl = None

logger = logging.getLogger(__name__)


class PortfolioAnalysisError(Exception):
    """Custom exception for portfolio analysis operations."""

    pass


def _check_dependencies():
    """Check if required dependencies are available."""
    if pd is None:
        raise ImportError("pandas is required for portfolio analysis")
    if np is None:
        raise ImportError("numpy is required for portfolio analysis")


def calculate_portfolio_barra_factors(
    holdings: pd.DataFrame,
    barra_factors: pd.DataFrame,
    weight_col: str = "占净值比例",
    stock_code_col: str = "股票代码_带后缀",
) -> pd.Series:
    """
    Calculate portfolio-level Barra factors from holdings and stock factors.

    This is essentially a matrix multiplication: Portfolio_Factor = Holdings_Weights * Stock_Factors

    Args:
        holdings: DataFrame with fund holdings (stocks and weights)
        barra_factors: DataFrame with stock-level Barra factors (indexed by stock code)
        weight_col: Column name containing portfolio weights
        stock_code_col: Column name containing stock codes

    Returns:
        Series with portfolio-level factor exposures

    Raises:
        PortfolioAnalysisError: If calculation fails
    """
    _check_dependencies()

    try:
        # Filter holdings for stocks that have factor data
        valid_holdings = holdings[
            holdings[stock_code_col].isin(barra_factors.index)
        ].copy()

        if valid_holdings.empty:
            logger.warning("No holdings found with available factor data")
            return pd.Series(dtype=float)

        # Ensure weights are numeric and sum to reasonable value
        valid_holdings[weight_col] = pd.to_numeric(
            valid_holdings[weight_col], errors="coerce"
        )
        valid_holdings = valid_holdings.dropna(subset=[weight_col])

        # Get factor data for the holdings
        stock_codes = valid_holdings[stock_code_col].tolist()
        factor_matrix = barra_factors.loc[stock_codes]

        # Select only numeric columns for factor calculation
        numeric_columns = factor_matrix.select_dtypes(include=[np.number]).columns
        factor_matrix_numeric = factor_matrix[numeric_columns]

        # Get weights as array
        weights = valid_holdings[weight_col].values

        # Calculate portfolio factors: w^T * F
        portfolio_factors = np.dot(weights, factor_matrix_numeric.values)

        # Create result series
        result = pd.Series(
            portfolio_factors,
            index=factor_matrix_numeric.columns,
            name="portfolio_factors",
        )

        # Add metadata
        result.attrs = {
            "total_weight": weights.sum(),
            "num_holdings": len(weights),
            "coverage_ratio": len(valid_holdings) / len(holdings),
            "calculation_date": datetime.now().isoformat(),
        }

        logger.info(
            f"Calculated portfolio factors for {len(weights)} holdings "
            f"(coverage: {result.attrs['coverage_ratio']:.2%})"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to calculate portfolio Barra factors: {e}")
        raise PortfolioAnalysisError(f"Portfolio factor calculation failed: {e}")


def create_benchmark_from_funds(
    fund_holdings_list: List[pd.DataFrame],
    weight_col: str = "占净值比例",
    stock_code_col: str = "股票代码_带后缀",
) -> pd.DataFrame:
    """
    Create a composite benchmark from multiple fund holdings by averaging stock weights.

    Args:
        fund_holdings_list: List of DataFrames with fund holdings
        weight_col: Column name containing portfolio weights
        stock_code_col: Column name containing stock codes

    Returns:
        DataFrame with aggregated benchmark holdings (average weights across funds)
    """
    _check_dependencies()

    # Combine all holdings
    combined = pd.concat(fund_holdings_list, axis=0, ignore_index=True)
    fund_codes = combined["fund_code"].unique()

    # Sum stock weights from all funds, then divide by number of funds to get average
    benchmark = combined.groupby(stock_code_col)[weight_col].sum().reset_index()
    num_funds = len(fund_codes)
    benchmark[weight_col] = benchmark[weight_col] / num_funds

    logger.info(
        f"Created benchmark with {len(benchmark)} unique holdings from {num_funds} funds"
    )
    return benchmark


def calculate_relative_risk_exposure(
    portfolio_factors: pd.Series,
    benchmark_factors: pd.Series,
    factor_names: Optional[List[str]] = None,
) -> pd.Series:
    """
    Calculate relative risk exposure between portfolio and benchmark.

    Relative exposure = Portfolio_Factor - Benchmark_Factor

    Args:
        portfolio_factors: Portfolio-level factor exposures
        benchmark_factors: Benchmark-level factor exposures
        factor_names: Specific factors to analyze (if None, use all common factors)

    Returns:
        Series with relative factor exposures
    """
    try:
        # Find common factors
        common_factors = portfolio_factors.index.intersection(benchmark_factors.index)

        if factor_names:
            # Filter for requested factors
            common_factors = common_factors.intersection(factor_names)

        if len(common_factors) == 0:
            logger.warning("No common factors found between portfolio and benchmark")
            return pd.Series(dtype=float)

        # Calculate relative exposures
        relative_exposure = (
            portfolio_factors.loc[common_factors]
            - benchmark_factors.loc[common_factors]
        )

        relative_exposure.name = "relative_exposure"

        # Add metadata
        relative_exposure.attrs = {
            "num_factors": len(common_factors),
            "max_absolute_exposure": abs(relative_exposure).max(),
            "calculation_date": datetime.now().isoformat(),
        }

        logger.info(f"Calculated relative exposure for {len(common_factors)} factors")
        return relative_exposure

    except Exception as e:
        logger.error(f"Failed to calculate relative risk exposure: {e}")
        raise PortfolioAnalysisError(f"Relative risk calculation failed: {e}")


def calculate_tracking_error(
    portfolio_returns: pd.Series, benchmark_returns: pd.Series, annualized: bool = True
) -> float:
    """
    Calculate tracking error between portfolio and benchmark returns.

    Args:
        portfolio_returns: Time series of portfolio returns
        benchmark_returns: Time series of benchmark returns
        annualized: Whether to annualize the tracking error

    Returns:
        Tracking error (standard deviation of excess returns)
    """
    try:
        # Align time series
        aligned_data = pd.DataFrame(
            {"portfolio": portfolio_returns, "benchmark": benchmark_returns}
        ).dropna()

        if len(aligned_data) < 2:
            logger.warning("Insufficient data for tracking error calculation")
            return 0.0

        # Calculate excess returns
        excess_returns = aligned_data["portfolio"] - aligned_data["benchmark"]

        # Calculate tracking error
        tracking_error = excess_returns.std()

        # Annualize if requested (assuming daily returns)
        if annualized:
            tracking_error *= np.sqrt(252)  # 252 trading days per year

        logger.info(f"Calculated tracking error: {tracking_error:.4f}")
        return tracking_error

    except Exception as e:
        logger.error(f"Failed to calculate tracking error: {e}")
        raise PortfolioAnalysisError(f"Tracking error calculation failed: {e}")


def calculate_information_ratio(
    portfolio_returns: pd.Series, benchmark_returns: pd.Series
) -> float:
    """
    Calculate information ratio (excess return / tracking error).

    Args:
        portfolio_returns: Time series of portfolio returns
        benchmark_returns: Time series of benchmark returns

    Returns:
        Information ratio
    """
    try:
        # Align time series
        aligned_data = pd.DataFrame(
            {"portfolio": portfolio_returns, "benchmark": benchmark_returns}
        ).dropna()

        if len(aligned_data) < 2:
            logger.warning("Insufficient data for information ratio calculation")
            return 0.0

        # Calculate excess returns
        excess_returns = aligned_data["portfolio"] - aligned_data["benchmark"]

        # Calculate mean excess return and tracking error
        mean_excess = excess_returns.mean()
        tracking_error = excess_returns.std()

        # Calculate information ratio
        if tracking_error == 0:
            return 0.0

        info_ratio = mean_excess / tracking_error

        # Annualize (assuming daily returns)
        info_ratio *= np.sqrt(252)

        logger.info(f"Calculated information ratio: {info_ratio:.4f}")
        return info_ratio

    except Exception as e:
        logger.error(f"Failed to calculate information ratio: {e}")
        raise PortfolioAnalysisError(f"Information ratio calculation failed: {e}")


def calculate_relative_performance_metrics(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.01,
) -> Dict[str, float]:
    """
    Calculate comprehensive relative performance metrics.

    Args:
        portfolio_returns: Time series of portfolio returns
        benchmark_returns: Time series of benchmark returns
        risk_free_rate: Risk-free rate for Sharpe ratio calculation

    Returns:
        Dictionary with performance metrics
    """
    try:
        # Align time series
        aligned_data = pd.DataFrame(
            {"portfolio": portfolio_returns, "benchmark": benchmark_returns}
        ).dropna()

        if len(aligned_data) < 2:
            logger.warning("Insufficient data for performance calculation")
            return {}

        portfolio_ret = aligned_data["portfolio"]
        benchmark_ret = aligned_data["benchmark"]
        excess_returns = portfolio_ret - benchmark_ret

        # Calculate metrics
        metrics = {
            # Return metrics
            "portfolio_total_return": (1 + portfolio_ret).prod() - 1,
            "benchmark_total_return": (1 + benchmark_ret).prod() - 1,
            "excess_return": excess_returns.sum(),
            "mean_excess_return": excess_returns.mean(),
            # Risk metrics
            "portfolio_volatility": portfolio_ret.std() * np.sqrt(252),
            "benchmark_volatility": benchmark_ret.std() * np.sqrt(252),
            "tracking_error": excess_returns.std() * np.sqrt(252),
            # Risk-adjusted metrics
            "information_ratio": calculate_information_ratio(
                portfolio_ret, benchmark_ret
            ),
            "correlation": portfolio_ret.corr(benchmark_ret),
            # Additional metrics
            "beta": portfolio_ret.cov(benchmark_ret) / benchmark_ret.var(),
            "alpha": excess_returns.mean() * 252,  # Annualized alpha
            "win_rate": (excess_returns > 0).mean(),
            "periods": len(aligned_data),
        }

        # Calculate Sharpe ratios if risk-free rate is available (assume 0 for now)

        metrics["portfolio_sharpe"] = (
            metrics["portfolio_total_return"] - risk_free_rate
        ) / metrics["portfolio_volatility"]
        metrics["benchmark_sharpe"] = (
            metrics["benchmark_total_return"] - risk_free_rate
        ) / metrics["benchmark_volatility"]

        logger.info(f"Calculated performance metrics for {metrics['periods']} periods")
        return metrics

    except Exception as e:
        logger.error(f"Failed to calculate performance metrics: {e}")
        raise PortfolioAnalysisError(f"Performance calculation failed: {e}")


def optimize_with_polars(
    holdings: pd.DataFrame,
    barra_factors: pd.DataFrame,
    weight_col: str = "占净值比例",
    stock_code_col: str = "股票代码_带后缀",
) -> pd.Series:
    """
    Fast portfolio factor calculation using Polars for large datasets.

    Args:
        holdings: DataFrame with fund holdings
        barra_factors: DataFrame with stock-level Barra factors
        weight_col: Column name containing portfolio weights
        stock_code_col: Column name containing stock codes

    Returns:
        Series with portfolio-level factor exposures
    """
    try:
        if pl is None:
            logger.warning("Polars not available, falling back to pandas")
            return calculate_portfolio_barra_factors(
                holdings, barra_factors, weight_col, stock_code_col
            )

        # Convert to Polars for faster computation
        holdings_pl = pl.from_pandas(holdings)
        factors_pl = pl.from_pandas(barra_factors.reset_index())

        # Join holdings with factors
        joined = holdings_pl.join(
            factors_pl, left_on=stock_code_col, right_on="stock_code", how="inner"
        )

        if joined.height == 0:
            logger.warning("No matching holdings found with factor data")
            return pd.Series(dtype=float)

        # Calculate weighted factors
        factor_cols = [
            col for col in joined.columns if col not in [stock_code_col, weight_col]
        ]

        portfolio_factors = {}
        for factor_col in factor_cols:
            if factor_col in barra_factors.columns:
                weighted_factor = joined.select(
                    [(pl.col(weight_col) * pl.col(factor_col)).sum()]
                ).item()
                portfolio_factors[factor_col] = weighted_factor

        result = pd.Series(portfolio_factors, name="portfolio_factors")

        logger.info(f"Fast calculation completed for {len(portfolio_factors)} factors")
        return result

    except Exception as e:
        logger.warning(f"Polars optimization failed, falling back to pandas: {e}")
        return calculate_portfolio_barra_factors(
            holdings, barra_factors, weight_col, stock_code_col
        )


# Example usage and testing
if __name__ == "__main__":

    def test_portfolio_analysis():
        """Test portfolio analysis functions."""
        try:
            print("Testing portfolio analysis functions...")

            # Create mock data for testing
            print("\n1. Creating mock data...")

            # Mock holdings
            holdings = pd.DataFrame(
                {
                    "股票代码_带后缀": ["000001.SZ", "600000.SH", "300001.SZ"],
                    "占净值比例": [0.3, 0.4, 0.3],
                    "股票名称": ["平安银行", "浦发银行", "特锐德"],
                }
            )

            # Mock Barra factors
            barra_factors = pd.DataFrame(
                {
                    "SIZE": [1.2, -0.5, 0.8],
                    "BETA": [1.1, 0.9, 1.3],
                    "BTOP": [0.2, -0.1, 0.5],
                },
                index=["000001.SZ", "600000.SH", "300001.SZ"],
            )

            print(f"Holdings shape: {holdings.shape}")
            print(f"Factors shape: {barra_factors.shape}")

            print("\n2. Calculating portfolio factors...")
            portfolio_factors = calculate_portfolio_barra_factors(
                holdings, barra_factors
            )
            print(f"Portfolio factors:\n{portfolio_factors}")

            print("\n3. Creating benchmark...")
            # Add fund_code column to holdings for the benchmark function
            holdings_with_fund_code = holdings.copy()
            holdings_with_fund_code["fund_code"] = "test_fund"
            benchmark_holdings = create_benchmark_from_funds([holdings_with_fund_code])
            print(f"Benchmark holdings shape: {benchmark_holdings.shape}")
            print(
                f"Benchmark total weight: {benchmark_holdings['占净值比例'].sum():.4f}"
            )

            benchmark_factors = calculate_portfolio_barra_factors(
                benchmark_holdings, barra_factors, stock_code_col="股票代码_带后缀"
            )

            print("\n4. Calculating relative exposure...")
            relative_exposure = calculate_relative_risk_exposure(
                portfolio_factors, benchmark_factors
            )
            print(f"Relative exposure:\n{relative_exposure}")

            print("\n5. Testing performance metrics...")
            # Mock return data
            dates = pd.date_range("2023-01-01", periods=100, freq="D")
            np.random.seed(42)
            portfolio_returns = pd.Series(
                np.random.normal(0.001, 0.02, 100), index=dates
            )
            benchmark_returns = pd.Series(
                np.random.normal(0.0008, 0.015, 100), index=dates
            )

            performance_metrics = calculate_relative_performance_metrics(
                portfolio_returns, benchmark_returns
            )
            print("Performance metrics:")
            for key, value in performance_metrics.items():
                print(f"  {key}: {value:.4f}")

            print("\nAll portfolio analysis tests completed successfully!")

        except Exception as e:
            print(f"Test failed: {e}")

    # Run the test
    test_portfolio_analysis()
