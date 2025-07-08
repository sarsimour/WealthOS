"""
Fund of Funds (FOF) portfolio analysis utilities.

This module provides functions for:
1. Calculating portfolio Barra factors from holdings
2. Computing relative risk exposure vs benchmarks
3. Analyzing relative performance vs benchmarks
4. Fast computation using optimized data structures
5. Portfolio risk metrics calculation
6. Diversification analysis based on factor exposures
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from datetime import datetime, timedelta
from decimal import Decimal

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


def get_fund_historical_data(
    fund_codes: List[str],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Fetch historical NAV and return data for funds.

    Args:
        fund_codes: List of fund codes
        start_date: Start date for data (defaults to 1 year ago)
        end_date: End date for data (defaults to today)

    Returns:
        DataFrame with historical NAV data

    Note:
        This is a placeholder implementation. In production, this would
        integrate with akshare or other data providers.
    """
    _check_dependencies()

    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()

    # Mock implementation - in production, use akshare
    logger.warning("Using mock fund data - integrate with akshare for production")

    dates = pd.date_range(start_date, end_date, freq="D")
    data = []

    for fund_code in fund_codes:
        # Generate mock NAV data with some realistic patterns
        np.random.seed(hash(fund_code) % 2**32)  # Deterministic but fund-specific

        base_nav = 1.0
        daily_returns = np.random.normal(0.0005, 0.015, len(dates))  # ~12% annual vol

        navs = [base_nav]
        for ret in daily_returns[1:]:
            navs.append(navs[-1] * (1 + ret))

        for date, nav in zip(dates, navs):
            data.append(
                {
                    "fund_code": fund_code,
                    "date": date,
                    "nav": nav,
                    "daily_return": (nav / navs[0] - 1) if nav != navs[0] else 0.0,
                }
            )

    df = pd.DataFrame(data)
    return df.set_index(["fund_code", "date"])


def calculate_portfolio_risk_metrics(
    portfolio_holdings: List[Dict], fund_historical_data: Optional[pd.DataFrame] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive portfolio risk metrics using historical data.

    Args:
        portfolio_holdings: List of holdings with fund_code, weight, fund_type
        fund_historical_data: Historical NAV data (optional, will fetch if not provided)

    Returns:
        Dictionary with risk metrics including volatility, correlations, VaR, etc.
    """
    _check_dependencies()

    try:
        fund_codes = [holding["fund_code"] for holding in portfolio_holdings]
        weights = np.array([holding["weight"] for holding in portfolio_holdings])

        # Fetch historical data if not provided
        if fund_historical_data is None:
            fund_historical_data = get_fund_historical_data(fund_codes)

        # Calculate returns matrix
        returns_data = []
        for fund_code in fund_codes:
            if fund_code in fund_historical_data.index.get_level_values(0):
                fund_data = fund_historical_data.loc[fund_code]
                returns = fund_data["daily_return"].dropna()
                if len(returns) > 0:
                    returns_data.append(returns)
                else:
                    # Fallback to estimated returns based on fund type
                    returns_data.append(
                        _estimate_fund_returns(fund_code, portfolio_holdings)
                    )
            else:
                returns_data.append(
                    _estimate_fund_returns(fund_code, portfolio_holdings)
                )

        # Align all return series to common dates
        if returns_data:
            returns_df = pd.concat(returns_data, axis=1, keys=fund_codes)
            returns_df = returns_df.dropna()

            if len(returns_df) > 20:  # Need sufficient data
                # Calculate portfolio returns
                portfolio_returns = (returns_df * weights).sum(axis=1)

                # Calculate risk metrics
                annual_vol = portfolio_returns.std() * np.sqrt(252)

                # Calculate correlation matrix
                corr_matrix = returns_df.corr()
                avg_correlation = corr_matrix.values[
                    np.triu_indices_from(corr_matrix.values, k=1)
                ].mean()

                # Calculate VaR (5% confidence level)
                var_95 = np.percentile(portfolio_returns, 5)

                # Calculate maximum drawdown
                cumulative_returns = (1 + portfolio_returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = drawdown.min()

                # Calculate Sharpe ratio (assuming 2% risk-free rate)
                sharpe_ratio = (portfolio_returns.mean() * 252 - 0.02) / annual_vol

                return {
                    "annual_volatility": annual_vol,
                    "average_correlation": avg_correlation,
                    "var_95_daily": var_95,
                    "max_drawdown": abs(max_drawdown),
                    "sharpe_ratio": sharpe_ratio,
                    "data_quality": "historical",
                    "observation_days": len(returns_df),
                }

        # Fallback to estimated metrics
        logger.warning("Insufficient historical data, using estimated risk metrics")
        return _estimate_portfolio_risk_metrics(portfolio_holdings)

    except Exception as e:
        logger.error(f"Failed to calculate portfolio risk metrics: {e}")
        return _estimate_portfolio_risk_metrics(portfolio_holdings)


def _estimate_fund_returns(fund_code: str, portfolio_holdings: List[Dict]) -> pd.Series:
    """Estimate fund returns based on fund type when historical data is unavailable."""
    # Find the fund in holdings to get its type
    fund_type = None
    for holding in portfolio_holdings:
        if holding["fund_code"] == fund_code:
            fund_type = holding.get("fund_type", "mixed")
            break

    # Generate estimated returns based on fund type
    dates = pd.date_range("2023-01-01", periods=252, freq="D")

    if fund_type == "equity":
        returns = np.random.normal(0.0008, 0.018, len(dates))  # ~15% vol
    elif fund_type == "bond":
        returns = np.random.normal(0.0003, 0.005, len(dates))  # ~5% vol
    elif fund_type == "money_market":
        returns = np.random.normal(0.0001, 0.002, len(dates))  # ~2% vol
    else:  # mixed or unknown
        returns = np.random.normal(0.0005, 0.012, len(dates))  # ~12% vol

    return pd.Series(returns, index=dates)


def _estimate_portfolio_risk_metrics(
    portfolio_holdings: List[Dict],
) -> Dict[str, float]:
    """Estimate portfolio risk metrics when historical data is unavailable."""
    # Simple estimation based on fund types and weights
    weights = np.array([holding["weight"] for holding in portfolio_holdings])

    estimated_vols = []
    for holding in portfolio_holdings:
        fund_type = holding.get("fund_type", "mixed")
        if fund_type == "equity":
            estimated_vols.append(0.15)
        elif fund_type == "bond":
            estimated_vols.append(0.05)
        elif fund_type == "money_market":
            estimated_vols.append(0.02)
        else:
            estimated_vols.append(0.12)

    estimated_vols = np.array(estimated_vols)

    # Simple portfolio volatility (assuming 0.6 average correlation)
    avg_correlation = 0.6
    portfolio_variance = np.sum(
        (weights * estimated_vols) ** 2
    ) + 2 * avg_correlation * np.sum(
        np.outer(weights * estimated_vols, weights * estimated_vols)[
            np.triu_indices(len(weights), k=1)
        ]
    )

    portfolio_vol = np.sqrt(portfolio_variance)

    return {
        "annual_volatility": portfolio_vol,
        "average_correlation": avg_correlation,
        "var_95_daily": -0.025,  # Rough estimate
        "max_drawdown": 0.15,  # Rough estimate
        "sharpe_ratio": 0.5,  # Rough estimate
        "data_quality": "estimated",
        "observation_days": 0,
    }


def calculate_diversification_metrics(
    portfolio_holdings: List[Dict],
    factor_exposures: Optional[pd.Series] = None,
    concentration_threshold: float = 0.4,
) -> Dict[str, float]:
    """
    Calculate comprehensive diversification metrics including factor concentration analysis.

    Args:
        portfolio_holdings: List of holdings with weights
        factor_exposures: Portfolio factor exposures from Barra analysis
        concentration_threshold: Threshold for considering factor exposure as concentrated

    Returns:
        Dictionary with diversification metrics
    """
    _check_dependencies()

    try:
        weights = np.array([holding["weight"] for holding in portfolio_holdings])

        # 1. Basic concentration metrics
        # Herfindahl-Hirschman Index
        hhi = np.sum(weights**2)

        # Effective number of holdings
        effective_holdings = 1 / hhi if hhi > 0 else 0

        # Concentration ratio (top 3 holdings)
        top_3_concentration = np.sum(np.sort(weights)[-3:])

        # 2. Diversification score (0-1, higher is better)
        max_possible_hhi = 1.0  # Single holding
        min_possible_hhi = 1.0 / len(weights)  # Equal weights

        if max_possible_hhi > min_possible_hhi:
            diversification_score = 1 - (hhi - min_possible_hhi) / (
                max_possible_hhi - min_possible_hhi
            )
        else:
            diversification_score = 1.0

        # 3. Factor concentration analysis
        factor_concentration_risks = []
        max_factor_exposure = 0.0

        if factor_exposures is not None and len(factor_exposures) > 0:
            # Check for concentrated factor exposures
            abs_exposures = np.abs(factor_exposures)
            max_factor_exposure = abs_exposures.max()

            # Identify concentrated factors
            concentrated_factors = abs_exposures[
                abs_exposures > concentration_threshold
            ]

            for factor_name, exposure in concentrated_factors.items():
                factor_concentration_risks.append(
                    {
                        "factor": factor_name,
                        "exposure": exposure,
                        "risk_level": "high" if abs(exposure) > 0.6 else "medium",
                    }
                )

        # 4. Asset type diversification
        fund_types = [
            holding.get("fund_type", "unknown") for holding in portfolio_holdings
        ]
        type_weights = {}
        for fund_type, weight in zip(fund_types, weights):
            type_weights[fund_type] = type_weights.get(fund_type, 0) + weight

        # Calculate asset type concentration
        type_hhi = sum(w**2 for w in type_weights.values())
        asset_type_diversification = 1 - type_hhi if len(type_weights) > 1 else 0

        return {
            "diversification_score": diversification_score,
            "herfindahl_index": hhi,
            "effective_holdings": effective_holdings,
            "top_3_concentration": top_3_concentration,
            "asset_type_diversification": asset_type_diversification,
            "max_factor_exposure": max_factor_exposure,
            "factor_concentration_count": len(factor_concentration_risks),
            "factor_concentration_risks": factor_concentration_risks,
            "overall_diversification_grade": _grade_diversification(
                diversification_score, len(factor_concentration_risks)
            ),
        }

    except Exception as e:
        logger.error(f"Failed to calculate diversification metrics: {e}")
        raise PortfolioAnalysisError(f"Diversification calculation failed: {e}")


def _grade_diversification(diversification_score: float, factor_risks: int) -> str:
    """Grade overall portfolio diversification."""
    if diversification_score > 0.8 and factor_risks == 0:
        return "A"  # Excellent
    elif diversification_score > 0.6 and factor_risks <= 1:
        return "B"  # Good
    elif diversification_score > 0.4 and factor_risks <= 2:
        return "C"  # Average
    elif diversification_score > 0.2 and factor_risks <= 3:
        return "D"  # Below Average
    else:
        return "F"  # Poor


def assess_factor_concentration(
    factor_exposures: pd.Series,
    benchmark_exposures: Optional[pd.Series] = None,
    risk_thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Dict]:
    """
    Assess portfolio factor concentration risks.

    Args:
        factor_exposures: Portfolio factor exposures
        benchmark_exposures: Benchmark factor exposures for comparison
        risk_thresholds: Custom risk thresholds for each factor

    Returns:
        Dictionary with factor concentration analysis
    """
    if risk_thresholds is None:
        risk_thresholds = {
            "SIZE": 0.5,
            "BETA": 0.4,
            "BTOP": 0.3,
            "MOMENTUM": 0.4,
            "VOLATILITY": 0.3,
            "GROWTH": 0.4,
            "EARNINGS_YIELD": 0.3,
            "LEVERAGE": 0.3,
        }

    concentration_analysis = {}

    for factor, exposure in factor_exposures.items():
        abs_exposure = abs(exposure)
        threshold = risk_thresholds.get(factor, 0.4)  # Default threshold

        # Determine risk level
        if abs_exposure > threshold * 1.5:
            risk_level = "HIGH"
        elif abs_exposure > threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Calculate relative exposure if benchmark available
        relative_exposure = None
        if benchmark_exposures is not None and factor in benchmark_exposures:
            relative_exposure = exposure - benchmark_exposures[factor]

        concentration_analysis[factor] = {
            "absolute_exposure": exposure,
            "relative_exposure": relative_exposure,
            "risk_level": risk_level,
            "threshold": threshold,
            "exceeds_threshold": abs_exposure > threshold,
            "interpretation": _interpret_factor_exposure(factor, exposure, risk_level),
        }

    return concentration_analysis


def _interpret_factor_exposure(factor: str, exposure: float, risk_level: str) -> str:
    """Provide human-readable interpretation of factor exposure."""
    abs_exp = abs(exposure)
    direction = "high" if exposure > 0 else "low"

    interpretations = {
        "SIZE": f"Portfolio tilts toward {direction} market cap stocks",
        "BETA": f"Portfolio has {direction} market sensitivity",
        "BTOP": f"Portfolio tilts toward {'value' if exposure > 0 else 'growth'} stocks",
        "MOMENTUM": f"Portfolio favors {'momentum' if exposure > 0 else 'contrarian'} strategies",
        "VOLATILITY": f"Portfolio tilts toward {direction} volatility stocks",
        "GROWTH": f"Portfolio tilts toward {'growth' if exposure > 0 else 'value'} stocks",
        "EARNINGS_YIELD": f"Portfolio tilts toward {direction} earnings yield stocks",
        "LEVERAGE": f"Portfolio tilts toward {direction} leverage companies",
    }

    base_interpretation = interpretations.get(
        factor, f"Portfolio has {direction} {factor} exposure"
    )

    if risk_level == "HIGH":
        return f"⚠️ {base_interpretation} (CONCENTRATED RISK)"
    elif risk_level == "MEDIUM":
        return f"⚡ {base_interpretation} (moderate concentration)"
    else:
        return f"✓ {base_interpretation} (well-balanced)"


def calculate_correlation_matrix(
    fund_codes: List[str], historical_data: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Calculate correlation matrix between funds.

    Args:
        fund_codes: List of fund codes
        historical_data: Historical return data

    Returns:
        Correlation matrix as DataFrame
    """
    _check_dependencies()

    if historical_data is None:
        historical_data = get_fund_historical_data(fund_codes)

    # Extract returns for each fund
    returns_data = {}
    for fund_code in fund_codes:
        if fund_code in historical_data.index.get_level_values(0):
            fund_data = historical_data.loc[fund_code]
            returns_data[fund_code] = fund_data["daily_return"].dropna()

    if returns_data:
        returns_df = pd.DataFrame(returns_data)
        return returns_df.corr()
    else:
        # Return identity matrix if no data
        return pd.DataFrame(
            np.eye(len(fund_codes)), index=fund_codes, columns=fund_codes
        )


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
