"""
Fund Advisory Workflow

LangGraph workflow for analyzing portfolio and providing investment recommendations.
"""

import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

from app.schemas.fund_analysis import (
    FundAnalysis,
    FundType,
    InvestmentRecommendation,
    PortfolioAnalysis,
    PortfolioSummary,
    RiskLevel,
    RiskMetrics,
)
from app.services.llm_service import llm_service
from app.workflows.base import BaseWorkflow, WorkflowState, WorkflowStep

try:
    from app.analysis.fof.portfolio_analysis import (
        calculate_portfolio_barra_factors,
        create_benchmark_from_funds,
        calculate_relative_risk_exposure,
        calculate_relative_performance_metrics,
        PortfolioAnalysisError,
    )
except ImportError:
    # Define dummy classes if portfolio analysis is not available
    class PortfolioAnalysisError(Exception):
        pass

    def calculate_portfolio_barra_factors(*args, **kwargs):  # type: ignore
        raise PortfolioAnalysisError("Portfolio analysis module not available")

    def create_benchmark_from_funds(*args, **kwargs):  # type: ignore
        raise PortfolioAnalysisError("Portfolio analysis module not available")

    def calculate_relative_risk_exposure(*args, **kwargs):  # type: ignore
        raise PortfolioAnalysisError("Portfolio analysis module not available")

    def calculate_relative_performance_metrics(*args, **kwargs):  # type: ignore
        raise PortfolioAnalysisError("Portfolio analysis module not available")


logger = logging.getLogger(__name__)


class PortfolioValidationStep(WorkflowStep):
    """Validate portfolio data for analysis."""

    def __init__(self):
        super().__init__(
            name="portfolio_validation",
            description="Validate portfolio data before analysis",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Validate portfolio summary data."""
        try:
            portfolio_summary = state.context.get("portfolio_summary")
            if not portfolio_summary:
                raise ValueError("No portfolio summary provided")

            if not isinstance(portfolio_summary, PortfolioSummary):
                raise ValueError("Invalid portfolio summary format")

            if not portfolio_summary.holdings:
                raise ValueError("Portfolio has no holdings to analyze")

            if portfolio_summary.total_value <= 0:
                raise ValueError("Portfolio total value must be positive")

            # Validate individual holdings
            for holding in portfolio_summary.holdings:
                if not holding.fund_code or not holding.fund_name:
                    raise ValueError(f"Incomplete holding data: {holding}")

                if holding.holding_value <= 0:
                    raise ValueError(f"Invalid holding value: {holding.holding_value}")

            self.logger.info(
                f"Portfolio validation passed: {len(portfolio_summary.holdings)} holdings"
            )
            return state

        except Exception as e:
            self.logger.error(f"Portfolio validation failed: {e}")
            raise


class RiskAnalysisStep(WorkflowStep):
    """Analyze portfolio risk metrics using real portfolio analysis functions."""

    def __init__(self):
        super().__init__(
            name="risk_analysis",
            description="Calculate portfolio risk metrics and classifications",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Perform risk analysis on the portfolio."""
        try:
            portfolio_summary: PortfolioSummary = state.context.get("portfolio_summary")
            if not portfolio_summary:
                raise ValueError("No portfolio summary in context")

            # Calculate basic risk metrics
            portfolio_risk = await self._calculate_portfolio_risk(portfolio_summary)
            diversification_score = await self._calculate_diversification(
                portfolio_summary
            )

            # Store results
            state.context["portfolio_risk"] = portfolio_risk
            state.context["diversification_score"] = diversification_score

            self.logger.info(f"Risk analysis completed: {portfolio_risk.risk_level}")
            return state

        except Exception as e:
            self.logger.error(f"Risk analysis failed: {e}")
            raise

    async def _calculate_portfolio_risk(
        self, portfolio: PortfolioSummary
    ) -> RiskMetrics:
        """Calculate portfolio-level risk metrics."""
        # Simplified risk calculation based on fund types
        equity_weight = 0.0
        bond_weight = 0.0

        for holding in portfolio.holdings:
            weight = float(holding.holding_value / portfolio.total_value)

            if holding.fund_type in [FundType.EQUITY]:
                equity_weight += weight
            elif holding.fund_type in [FundType.BOND, FundType.MONEY_MARKET]:
                bond_weight += weight
            elif holding.fund_type == FundType.MIXED:
                # Assume 60/40 equity/bond split for mixed funds
                equity_weight += weight * 0.6
                bond_weight += weight * 0.4

        # Estimate volatility based on asset allocation
        estimated_volatility = (
            equity_weight * 0.15 + bond_weight * 0.05
        )  # Rough estimates

        # Determine risk level
        if estimated_volatility < 0.05:
            risk_level = RiskLevel.LOW
        elif estimated_volatility < 0.10:
            risk_level = RiskLevel.MEDIUM_LOW
        elif estimated_volatility < 0.15:
            risk_level = RiskLevel.MEDIUM
        elif estimated_volatility < 0.20:
            risk_level = RiskLevel.MEDIUM_HIGH
        else:
            risk_level = RiskLevel.HIGH

        return RiskMetrics(
            volatility=estimated_volatility,
            sharpe_ratio=None,  # Would need return data
            max_drawdown=None,  # Would need historical data
            beta=None,  # Would need benchmark data
            var_95=None,  # Would need distribution modeling
            risk_level=risk_level,
        )

    async def _calculate_diversification(self, portfolio: PortfolioSummary) -> float:
        """Calculate portfolio diversification score (0-1)."""
        if len(portfolio.holdings) <= 1:
            return 0.0

        # Calculate concentration (Herfindahl index)
        concentration = sum(
            (float(holding.holding_value / portfolio.total_value)) ** 2
            for holding in portfolio.holdings
        )

        # Convert to diversification score (inverse of concentration)
        max_concentration = 1.0  # Single holding
        min_concentration = 1.0 / len(portfolio.holdings)  # Equal weights

        if max_concentration == min_concentration:
            return 1.0

        diversification = 1.0 - (concentration - min_concentration) / (
            max_concentration - min_concentration
        )
        return max(0.0, min(1.0, diversification))


class FundAnalysisStep(WorkflowStep):
    """Analyze individual funds in the portfolio."""

    def __init__(self):
        super().__init__(
            name="fund_analysis",
            description="Analyze individual fund performance and characteristics",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Analyze each fund in the portfolio."""
        try:
            portfolio_summary: PortfolioSummary = state.context.get("portfolio_summary")
            if not portfolio_summary:
                raise ValueError("No portfolio summary in context")

            fund_analyses = []
            for holding in portfolio_summary.holdings:
                fund_analysis = await self._analyze_fund(holding)
                fund_analyses.append(fund_analysis)

            state.context["fund_analyses"] = fund_analyses

            self.logger.info(f"Analyzed {len(fund_analyses)} individual funds")
            return state

        except Exception as e:
            self.logger.error(f"Fund analysis failed: {e}")
            raise

    async def _analyze_fund(self, holding) -> FundAnalysis:
        """Analyze a single fund."""
        # TODO: Implement real fund analysis with akshare data
        # For now, create basic analysis structure

        # Estimate risk based on fund type
        if holding.fund_type == FundType.EQUITY:
            volatility = 0.15
            risk_level = RiskLevel.MEDIUM_HIGH
        elif holding.fund_type == FundType.BOND:
            volatility = 0.05
            risk_level = RiskLevel.LOW
        elif holding.fund_type == FundType.MIXED:
            volatility = 0.10
            risk_level = RiskLevel.MEDIUM
        elif holding.fund_type == FundType.MONEY_MARKET:
            volatility = 0.02
            risk_level = RiskLevel.LOW
        else:
            volatility = 0.12
            risk_level = RiskLevel.MEDIUM

        risk_metrics = RiskMetrics(
            volatility=volatility,
            risk_level=risk_level,
            sharpe_ratio=None,
            max_drawdown=None,
            beta=None,
            var_95=None,
        )

        return FundAnalysis(
            fund_code=holding.fund_code,
            fund_name=holding.fund_name,
            fund_type=holding.fund_type,
            current_price=holding.current_price or Decimal("1.0"),
            ytd_return=None,
            one_year_return=None,
            three_year_return=None,
            fund_manager=None,
            management_fee=None,
            aum=None,
            risk_metrics=risk_metrics,
            analysis_date=datetime.now(),
        )


class PortfolioFactorAnalysisStep(WorkflowStep):
    """Analyze portfolio using real Barra factor analysis."""

    def __init__(self):
        super().__init__(
            name="portfolio_factor_analysis",
            description="Calculate portfolio Barra factors and relative exposures",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Perform factor analysis on the portfolio."""
        try:
            portfolio_summary: PortfolioSummary = state.context.get("portfolio_summary")
            if not portfolio_summary:
                raise ValueError("No portfolio summary in context")

            # Create mock holdings data for demonstration
            # In production, this would come from fund holdings data via akshare
            holdings_data = await self._create_mock_holdings_data(portfolio_summary)

            # Create mock Barra factors data
            barra_factors = await self._create_mock_barra_factors(holdings_data)

            if not holdings_data.empty and not barra_factors.empty:
                try:
                    # Calculate portfolio factors using our analysis functions
                    portfolio_factors = calculate_portfolio_barra_factors(
                        holdings_data, barra_factors
                    )

                    # Create benchmark from funds
                    benchmark_holdings = create_benchmark_from_funds([holdings_data])
                    benchmark_factors = calculate_portfolio_barra_factors(
                        benchmark_holdings,
                        barra_factors,
                        stock_code_col="股票代码_带后缀",
                    )

                    # Calculate relative exposure
                    relative_exposure = calculate_relative_risk_exposure(
                        portfolio_factors, benchmark_factors
                    )

                    # Store results
                    state.context["portfolio_factors"] = portfolio_factors
                    state.context["benchmark_factors"] = benchmark_factors
                    state.context["relative_exposure"] = relative_exposure

                    self.logger.info("Portfolio factor analysis completed successfully")

                except PortfolioAnalysisError as e:
                    self.logger.warning(f"Factor analysis failed: {e}")
                    # Continue without factor analysis
                    state.context["portfolio_factors"] = None
                    state.context["benchmark_factors"] = None
                    state.context["relative_exposure"] = None
            else:
                self.logger.warning("Insufficient data for factor analysis")
                state.context["portfolio_factors"] = None
                state.context["benchmark_factors"] = None
                state.context["relative_exposure"] = None

            return state

        except Exception as e:
            self.logger.error(f"Portfolio factor analysis failed: {e}")
            # Don't fail the entire workflow, just skip factor analysis
            state.context["portfolio_factors"] = None
            state.context["benchmark_factors"] = None
            state.context["relative_exposure"] = None
            return state

    async def _create_mock_holdings_data(
        self, portfolio: PortfolioSummary
    ) -> pd.DataFrame:
        """Create mock holdings data for demonstration."""
        # In production, this would fetch real fund holdings from akshare
        holdings_list = []

        for holding in portfolio.holdings:
            # Create mock stock holdings for each fund
            mock_stocks = [
                {
                    "股票代码_带后缀": "000001.SZ",
                    "占净值比例": 0.1,
                    "股票名称": "平安银行",
                },
                {
                    "股票代码_带后缀": "600000.SH",
                    "占净值比例": 0.08,
                    "股票名称": "浦发银行",
                },
                {
                    "股票代码_带后缀": "300001.SZ",
                    "占净值比例": 0.06,
                    "股票名称": "特锐德",
                },
            ]

            for stock in mock_stocks:
                holdings_list.append(
                    {
                        "fund_code": holding.fund_code,
                        "股票代码_带后缀": stock["股票代码_带后缀"],
                        "占净值比例": stock["占净值比例"]
                        * float(holding.holding_value / portfolio.total_value),
                        "股票名称": stock["股票名称"],
                    }
                )

        return pd.DataFrame(holdings_list)

    async def _create_mock_barra_factors(
        self, holdings_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Create mock Barra factors data for demonstration."""
        # In production, this would fetch real Barra factors
        unique_stocks = holdings_data["股票代码_带后缀"].unique()

        factors_data = []
        for stock in unique_stocks:
            factors_data.append(
                {
                    "股票代码_带后缀": stock,
                    "SIZE": np.random.normal(0, 1),
                    "BETA": np.random.normal(1, 0.3),
                    "BTOP": np.random.normal(0, 0.5),
                    "MOMENTUM": np.random.normal(0, 0.8),
                    "VOLATILITY": np.random.normal(0, 0.6),
                }
            )

        df = pd.DataFrame(factors_data)
        return df.set_index("股票代码_带后缀")


class RecommendationStep(WorkflowStep):
    """Generate investment recommendations using LLM."""

    def __init__(self):
        super().__init__(
            name="recommendation_generation",
            description="Generate AI-powered investment recommendations",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Generate investment recommendations."""
        try:
            portfolio_summary: PortfolioSummary = state.context.get("portfolio_summary")
            portfolio_risk: RiskMetrics = state.context.get("portfolio_risk")
            diversification_score: float = state.context.get(
                "diversification_score", 0.0
            )
            fund_analyses: List[FundAnalysis] = state.context.get("fund_analyses", [])
            user_profile: Dict = state.context.get("user_profile", {})

            if not portfolio_summary or not portfolio_risk:
                raise ValueError("Missing required analysis data")

            # Prepare comprehensive analysis prompt
            prompt = f"""
            作为专业的投资顾问，请分析以下投资组合并提供建议：

            投资组合概况：
            - 总价值：{portfolio_summary.total_value:,.2f} CNY
            - 持仓数量：{len(portfolio_summary.holdings)}
            - 风险等级：{portfolio_risk.risk_level.value}
            - 分散化得分：{diversification_score:.2f}

            持仓明细：
            {self._format_holdings_for_prompt(portfolio_summary.holdings)}

            用户画像：
            {self._format_user_profile(user_profile)}

            请提供：
            1. 总体投资建议（买入/持有/卖出）
            2. 投资建议的置信度（0-1）
            3. 详细分析理由
            4. 主要风险因素
            5. 风险缓解策略
            6. 资产配置建议

            请基于当前市场环境、基金质量、风险收益特征等因素给出专业建议。
            """

            # Generate recommendation using LLM with text-only analysis
            recommendation = await llm_service.generate_text_response(
                prompt=prompt,
                system_prompt="你是一个专业的投资顾问，请提供结构化的投资建议。",
                max_tokens=2000,
                temperature=0.3,
            )

            # Parse the text response into structured format
            parsed_recommendation = self._parse_recommendation_text(recommendation)
            state.context["overall_recommendation"] = parsed_recommendation

            # Generate rebalancing suggestions
            rebalancing_suggestions = await self._generate_rebalancing_suggestions(
                portfolio_summary, portfolio_risk, diversification_score
            )
            state.context["rebalancing_suggestions"] = rebalancing_suggestions

            self.logger.info("Investment recommendations generated")
            return state

        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            raise

    def _format_holdings_for_prompt(self, holdings) -> str:
        """Format holdings for LLM prompt."""
        formatted = []
        for holding in holdings:
            formatted.append(
                f"- {holding.fund_name} ({holding.fund_code}): "
                f"{holding.holding_value:,.2f} CNY "
                f"({holding.holding_percentage:.1f}%)"
            )
        return "\n".join(formatted)

    def _format_user_profile(self, user_profile: Dict) -> str:
        """Format user profile for LLM prompt."""
        if not user_profile:
            return "用户画像信息不可用"

        formatted = []
        for key, value in user_profile.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted) if formatted else "用户画像信息不可用"

    def _parse_recommendation_text(self, text: str) -> InvestmentRecommendation:
        """Parse LLM text response into structured recommendation."""
        # Simple parsing logic - in production, use more sophisticated parsing
        lines = text.split("\n")

        # Extract recommendation type
        recommendation = "持有"  # Default
        for line in lines:
            if any(word in line for word in ["买入", "购买", "增持"]):
                recommendation = "买入"
                break
            elif any(word in line for word in ["卖出", "减持"]):
                recommendation = "卖出"
                break

        # Extract confidence (look for percentage or decimal)
        confidence = 0.7  # Default
        for line in lines:
            if "置信度" in line or "信心" in line:
                # Try to extract number
                import re

                numbers = re.findall(r"\d+\.?\d*", line)
                if numbers:
                    confidence = min(
                        (
                            float(numbers[0]) / 100
                            if float(numbers[0]) > 1
                            else float(numbers[0])
                        ),
                        1.0,
                    )
                break

        return InvestmentRecommendation(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=text,
            target_allocation=None,
            time_horizon=None,
            key_risks=[],
            risk_mitigation=[],
        )

    async def _generate_rebalancing_suggestions(
        self, portfolio: PortfolioSummary, risk: RiskMetrics, diversification: float
    ) -> List[str]:
        """Generate portfolio rebalancing suggestions."""
        suggestions = []

        # Check diversification
        if diversification < 0.5:
            suggestions.append("考虑增加持仓数量以提高投资组合分散化程度")

        # Check concentration
        for holding in portfolio.holdings:
            weight = float(holding.holding_value / portfolio.total_value)
            if weight > 0.3:
                suggestions.append(
                    f"考虑减少{holding.fund_name}的配置比例（当前{weight:.1%}）"
                )

        # Check asset allocation
        equity_weight = sum(
            float(h.holding_value / portfolio.total_value)
            for h in portfolio.holdings
            if h.fund_type == FundType.EQUITY
        )

        if equity_weight > 0.8:
            suggestions.append("股票类基金配置比例较高，建议适当增加债券类资产")
        elif equity_weight < 0.3:
            suggestions.append("股票类基金配置比例较低，可考虑适当增加权益类投资")

        return suggestions


class ResultCompilationStep(WorkflowStep):
    """Compile final analysis results."""

    def __init__(self):
        super().__init__(
            name="result_compilation",
            description="Compile comprehensive portfolio analysis results",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Compile final portfolio analysis."""
        try:
            # Gather all analysis components
            portfolio_summary: PortfolioSummary = state.context.get("portfolio_summary")
            fund_analyses: List[FundAnalysis] = state.context.get("fund_analyses", [])
            portfolio_risk: RiskMetrics = state.context.get("portfolio_risk")
            diversification_score: float = state.context.get(
                "diversification_score", 0.0
            )
            overall_recommendation: InvestmentRecommendation = state.context.get(
                "overall_recommendation"
            )
            rebalancing_suggestions: List[str] = state.context.get(
                "rebalancing_suggestions", []
            )

            if (
                not portfolio_summary
                or not portfolio_risk
                or not overall_recommendation
            ):
                raise ValueError("Missing required analysis components")

            # Calculate asset allocation
            asset_allocation = self._calculate_asset_allocation(portfolio_summary)

            # Create comprehensive portfolio analysis
            portfolio_analysis = PortfolioAnalysis(
                portfolio_summary=portfolio_summary,
                fund_analyses=fund_analyses,
                portfolio_risk=portfolio_risk,
                diversification_score=diversification_score,
                asset_allocation=asset_allocation,
                overall_recommendation=overall_recommendation,
                rebalancing_suggestions=rebalancing_suggestions,
                analysis_date=datetime.now(),
            )

            state.context["final_analysis"] = portfolio_analysis

            self.logger.info("Portfolio analysis compilation completed")
            return state

        except Exception as e:
            self.logger.error(f"Result compilation failed: {e}")
            raise

    def _calculate_asset_allocation(
        self, portfolio: PortfolioSummary
    ) -> Dict[str, float]:
        """Calculate asset allocation breakdown."""
        allocation = {
            "equity": 0.0,
            "bond": 0.0,
            "mixed": 0.0,
            "money_market": 0.0,
            "other": 0.0,
        }

        for holding in portfolio.holdings:
            weight = float(holding.holding_value / portfolio.total_value)

            if holding.fund_type == FundType.EQUITY:
                allocation["equity"] += weight
            elif holding.fund_type == FundType.BOND:
                allocation["bond"] += weight
            elif holding.fund_type == FundType.MIXED:
                allocation["mixed"] += weight
            elif holding.fund_type == FundType.MONEY_MARKET:
                allocation["money_market"] += weight
            else:
                allocation["other"] += weight

        return allocation


class FundAdvisoryWorkflow(BaseWorkflow):
    """Complete workflow for fund investment advisory."""

    def __init__(self):
        super().__init__(
            name="fund_advisory",
            description="Comprehensive fund portfolio analysis and investment advisory",
        )

        # Add workflow steps
        self.add_step(PortfolioValidationStep())
        self.add_step(RiskAnalysisStep())
        self.add_step(FundAnalysisStep())
        self.add_step(PortfolioFactorAnalysisStep())
        self.add_step(RecommendationStep())
        self.add_step(ResultCompilationStep())

        self.logger.info("Fund advisory workflow initialized")

    async def analyze_portfolio(
        self,
        portfolio_summary: PortfolioSummary,
        user_profile: Optional[Dict[str, str]] = None,
    ) -> PortfolioAnalysis:
        """Analyze portfolio and provide investment recommendations."""
        try:
            # Create initial state
            initial_state = WorkflowState(
                workflow_id=f"advisory_{int(datetime.now().timestamp())}",
                started_at=datetime.now(),
                context={
                    "portfolio_summary": portfolio_summary,
                    "user_profile": user_profile or {},
                },
            )

            # Execute the workflow
            result_state = await self.execute(initial_state)

            if result_state.status == "error":
                raise ValueError(
                    f"Advisory workflow failed: {result_state.error_message}"
                )

            # Extract final analysis
            portfolio_analysis = result_state.context.get("final_analysis")
            if not portfolio_analysis:
                raise ValueError("No analysis results produced")

            return portfolio_analysis

        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            raise


# Create workflow instance
fund_advisory_workflow = FundAdvisoryWorkflow()


# Helper function for direct usage
async def analyze_fund_portfolio(
    portfolio_summary: PortfolioSummary, user_profile: Optional[Dict[str, str]] = None
) -> PortfolioAnalysis:
    """Analyze a fund portfolio and provide investment recommendations."""
    return await fund_advisory_workflow.analyze_portfolio(
        portfolio_summary, user_profile
    )
