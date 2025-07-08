"""
Fund Advisory Workflow

This workflow provides comprehensive fund portfolio analysis and investment advice
using a character-based advisor approach.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.workflows.base import BaseWorkflow, WorkflowState
from app.schemas.fund_analysis import (
    FundAnalysis,
    InvestmentRecommendation,
    PortfolioAnalysis,
    PortfolioSummary,
    RiskLevel,
    RiskMetrics,
)
from app.services.llm_service import llm_service, character_advisor
from app.analysis.fof.portfolio_analysis import (
    calculate_portfolio_risk_metrics,
    calculate_diversification_metrics,
    assess_factor_concentration,
    calculate_relative_risk_exposure,
)
from app.schemas.character import CharacterState

logger = logging.getLogger(__name__)


class FundAdvisoryWorkflow(BaseWorkflow):
    """
    Comprehensive fund advisory workflow with character-based advice.

    This workflow:
    1. Validates portfolio data
    2. Calculates risk metrics using portfolio analysis
    3. Analyzes individual funds
    4. Performs factor analysis
    5. Generates character-based recommendations
    6. Compiles final results
    """

    def __init__(self):
        super().__init__(
            name="fund_advisory", description="Character-based fund advisory workflow"
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the workflow graph."""
        graph = StateGraph(WorkflowState)

        # Add nodes
        graph.add_node("validate_portfolio", self._validate_portfolio)
        graph.add_node("calculate_risk", self._calculate_risk_metrics)
        graph.add_node("analyze_funds", self._analyze_individual_funds)
        graph.add_node("factor_analysis", self._perform_factor_analysis)
        graph.add_node(
            "generate_recommendations", self._generate_character_recommendations
        )
        graph.add_node("compile_results", self._compile_results)

        # Add edges
        graph.add_edge("validate_portfolio", "calculate_risk")
        graph.add_edge("calculate_risk", "analyze_funds")
        graph.add_edge("analyze_funds", "factor_analysis")
        graph.add_edge("factor_analysis", "generate_recommendations")
        graph.add_edge("generate_recommendations", "compile_results")
        graph.add_edge("compile_results", END)

        # Set entry point
        graph.set_entry_point("validate_portfolio")

        return graph

    async def _validate_portfolio(self, state: WorkflowState) -> WorkflowState:
        """Validate portfolio data and structure."""
        try:
            portfolio_data = state.context.get("portfolio_data")
            if not portfolio_data:
                raise ValueError("No portfolio data provided")

            # Validate portfolio structure
            if not isinstance(portfolio_data, PortfolioSummary):
                raise ValueError("Portfolio data must be a PortfolioSummary object")

            if not portfolio_data.holdings or len(portfolio_data.holdings) == 0:
                raise ValueError("Portfolio must have at least one holding")

            # Validate holdings - calculate weights from holding values
            total_value = portfolio_data.total_value
            total_percentage = sum(
                holding.holding_percentage or 0 for holding in portfolio_data.holdings
            )
            if total_percentage <= 0:
                raise ValueError("Portfolio holdings must have positive percentages")

            logger.info(
                f"Portfolio validation passed: {len(portfolio_data.holdings)} holdings, total percentage: {total_percentage:.2%}"
            )

            state.context["validation_status"] = "passed"
            state.context["validation_message"] = (
                f"Portfolio validated successfully with {len(portfolio_data.holdings)} holdings"
            )

            return state

        except Exception as e:
            logger.error(f"Portfolio validation failed: {e}")
            state.context["validation_status"] = "failed"
            state.context["validation_message"] = str(e)
            state.context["error"] = str(e)
            return state

    async def _calculate_risk_metrics(self, state: WorkflowState) -> WorkflowState:
        """Calculate comprehensive risk metrics using portfolio analysis."""
        try:
            portfolio_data = state.get("portfolio_data")
            if not portfolio_data:
                raise ValueError("No portfolio data available")

            # Convert holdings to format expected by portfolio analysis
            holdings_list = []
            for holding in portfolio_data.holdings:
                holdings_list.append(
                    {
                        "fund_code": holding.fund_code,
                        "weight": holding.weight,
                        "fund_type": getattr(holding, "fund_type", "mixed"),
                        "fund_name": holding.fund_name,
                    }
                )

            # Calculate risk metrics using portfolio analysis
            risk_metrics = calculate_portfolio_risk_metrics(holdings_list)

            # Map to our risk level enum
            annual_vol = risk_metrics.get("annual_volatility", 0.12)
            if annual_vol < 0.05:
                risk_level = RiskLevel.LOW
            elif annual_vol < 0.10:
                risk_level = RiskLevel.MEDIUM_LOW
            elif annual_vol < 0.15:
                risk_level = RiskLevel.MEDIUM
            elif annual_vol < 0.20:
                risk_level = RiskLevel.MEDIUM_HIGH
            else:
                risk_level = RiskLevel.HIGH

            # Create risk metrics object
            portfolio_risk = RiskMetrics(
                risk_level=risk_level,
                volatility=annual_vol,
                sharpe_ratio=risk_metrics.get("sharpe_ratio", 0.5),
                max_drawdown=risk_metrics.get("max_drawdown", 0.15),
                var_95=risk_metrics.get("var_95_daily", -0.025),
                correlation_avg=risk_metrics.get("average_correlation", 0.6),
                data_quality=risk_metrics.get("data_quality", "estimated"),
            )

            logger.info(
                f"Risk analysis completed: {risk_level.value} risk level, {annual_vol:.2%} volatility"
            )

            state["portfolio_risk"] = portfolio_risk
            state["risk_calculation_status"] = "completed"

            return state

        except Exception as e:
            logger.error(f"Risk calculation failed: {e}")
            state["risk_calculation_status"] = "failed"
            state["error"] = str(e)
            return state

    async def _analyze_individual_funds(self, state: WorkflowState) -> WorkflowState:
        """Analyze individual funds in the portfolio."""
        try:
            portfolio_data = state.get("portfolio_data")
            if not portfolio_data:
                raise ValueError("No portfolio data available")

            fund_analyses = []

            for holding in portfolio_data.holdings:
                try:
                    # Create analysis prompt for each fund
                    analysis_prompt = f"""
                    Analyze this fund holding:
                    
                    Fund: {holding.fund_name} ({holding.fund_code})
                    Weight in Portfolio: {holding.weight:.2%}
                    Current Value: ¥{holding.current_value:,.2f}
                    
                    Provide analysis covering:
                    1. Fund type and investment strategy
                    2. Risk characteristics
                    3. Performance expectations
                    4. Suitability for current portfolio
                    
                    Keep analysis concise and practical.
                    """

                    # Generate analysis using LLM
                    analysis_text = await llm_service.generate_text_response(
                        prompt=analysis_prompt,
                        system_prompt="You are a fund analysis expert. Provide concise, practical analysis.",
                        max_tokens=500,
                        temperature=0.3,
                    )

                    # Create fund analysis object
                    fund_analysis = FundAnalysis(
                        fund_code=holding.fund_code,
                        fund_name=holding.fund_name,
                        analysis_summary=analysis_text,
                        risk_rating="Medium",  # Default, could be enhanced
                        recommendation="Hold",  # Default, could be enhanced
                        weight_in_portfolio=holding.weight,
                    )

                    fund_analyses.append(fund_analysis)

                except Exception as e:
                    logger.warning(f"Failed to analyze fund {holding.fund_code}: {e}")
                    # Create minimal analysis
                    fund_analysis = FundAnalysis(
                        fund_code=holding.fund_code,
                        fund_name=holding.fund_name,
                        analysis_summary=f"Analysis unavailable for {holding.fund_name}",
                        risk_rating="Unknown",
                        recommendation="Review",
                        weight_in_portfolio=holding.weight,
                    )
                    fund_analyses.append(fund_analysis)

            logger.info(
                f"Individual fund analysis completed for {len(fund_analyses)} funds"
            )

            state["fund_analyses"] = fund_analyses
            state["fund_analysis_status"] = "completed"

            return state

        except Exception as e:
            logger.error(f"Fund analysis failed: {e}")
            state["fund_analysis_status"] = "failed"
            state["error"] = str(e)
            return state

    async def _perform_factor_analysis(self, state: WorkflowState) -> WorkflowState:
        """Perform portfolio factor analysis and diversification assessment."""
        try:
            portfolio_data = state.get("portfolio_data")
            if not portfolio_data:
                raise ValueError("No portfolio data available")

            # Convert holdings for analysis
            holdings_list = []
            for holding in portfolio_data.holdings:
                holdings_list.append(
                    {
                        "fund_code": holding.fund_code,
                        "weight": holding.weight,
                        "fund_type": getattr(holding, "fund_type", "mixed"),
                        "fund_name": holding.fund_name,
                    }
                )

            # Calculate diversification metrics
            diversification_metrics = calculate_diversification_metrics(holdings_list)

            # Mock factor exposures for now (in production, this would come from Barra analysis)
            import pandas as pd

            factor_exposures = pd.Series(
                {
                    "SIZE": 0.2,
                    "BETA": 0.1,
                    "GROWTH": 0.3,
                    "MOMENTUM": -0.1,
                    "VOLATILITY": 0.15,
                }
            )

            # Assess factor concentration
            factor_concentration = assess_factor_concentration(factor_exposures)

            # Create factor analysis summary
            factor_analysis = {
                "diversification_score": diversification_metrics.get(
                    "diversification_score", 0.5
                ),
                "diversification_grade": diversification_metrics.get(
                    "overall_diversification_grade", "C"
                ),
                "concentration_risks": diversification_metrics.get(
                    "factor_concentration_risks", []
                ),
                "factor_exposures": factor_exposures.to_dict(),
                "factor_concentration": factor_concentration,
                "effective_holdings": diversification_metrics.get(
                    "effective_holdings", 0
                ),
                "top_3_concentration": diversification_metrics.get(
                    "top_3_concentration", 0
                ),
            }

            logger.info(
                f"Factor analysis completed: {factor_analysis['diversification_grade']} diversification grade"
            )

            state["factor_analysis"] = factor_analysis
            state["factor_analysis_status"] = "completed"

            return state

        except Exception as e:
            logger.error(f"Factor analysis failed: {e}")
            state["factor_analysis_status"] = "failed"
            state["error"] = str(e)
            return state

    async def _generate_character_recommendations(
        self, state: WorkflowState
    ) -> WorkflowState:
        """Generate character-based investment recommendations."""
        try:
            portfolio_data = state.get("portfolio_data")
            portfolio_risk = state.get("portfolio_risk")
            fund_analyses = state.get("fund_analyses", [])
            factor_analysis = state.get("factor_analysis", {})

            if not all([portfolio_data, portfolio_risk]):
                raise ValueError("Missing required analysis data")

            # Prepare data for character advisor
            portfolio_summary = {
                "total_value": portfolio_data.total_value,
                "total_holdings": len(portfolio_data.holdings),
                "holdings_summary": ", ".join(
                    [
                        f"{h.fund_name} ({h.weight:.1%})"
                        for h in portfolio_data.holdings[:3]
                    ]
                ),
            }

            analysis_results = {
                "risk_level": portfolio_risk.risk_level.value,
                "volatility": portfolio_risk.volatility,
                "diversification_score": factor_analysis.get(
                    "diversification_score", 0.5
                ),
                "diversification_grade": factor_analysis.get(
                    "diversification_grade", "C"
                ),
                "factor_exposures": factor_analysis.get("factor_exposures", {}),
                "concentration_risks": factor_analysis.get("concentration_risks", []),
            }

            # Generate character-based advice
            character_advice = await character_advisor.analyze_portfolio_with_character(
                portfolio_data=portfolio_summary,
                analysis_results=analysis_results,
                state=CharacterState.ADVISING,
            )

            # Create recommendation object
            recommendation = InvestmentRecommendation(
                summary=character_advice,
                action_items=[
                    "Review portfolio diversification",
                    "Consider rebalancing if needed",
                    "Monitor risk levels regularly",
                ],
                risk_warnings=[
                    "Past performance doesn't guarantee future results",
                    "All investments carry risk",
                ],
                confidence_level=0.8,
                generated_at=datetime.now(),
            )

            logger.info("Character-based recommendations generated successfully")

            state["recommendations"] = recommendation
            state["recommendation_status"] = "completed"

            return state

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            state["recommendation_status"] = "failed"
            state["error"] = str(e)
            return state

    async def _compile_results(self, state: WorkflowState) -> WorkflowState:
        """Compile final portfolio analysis results."""
        try:
            portfolio_data = state.get("portfolio_data")
            portfolio_risk = state.get("portfolio_risk")
            fund_analyses = state.get("fund_analyses", [])
            factor_analysis = state.get("factor_analysis", {})
            recommendations = state.get("recommendations")

            if not all([portfolio_data, portfolio_risk, recommendations]):
                raise ValueError("Missing required analysis components")

            # Create comprehensive portfolio analysis
            portfolio_analysis = PortfolioAnalysis(
                portfolio_summary=portfolio_data,
                risk_metrics=portfolio_risk,
                fund_analyses=fund_analyses,
                recommendations=recommendations,
                analysis_date=datetime.now(),
                total_score=self._calculate_overall_score(
                    portfolio_risk, factor_analysis
                ),
                key_insights=[
                    f"Portfolio risk level: {portfolio_risk.risk_level.value}",
                    f"Diversification grade: {factor_analysis.get('diversification_grade', 'N/A')}",
                    f"Total holdings: {len(portfolio_data.holdings)}",
                    f"Volatility: {portfolio_risk.volatility:.2%}",
                ],
            )

            logger.info("Portfolio analysis compilation completed successfully")

            state["final_analysis"] = portfolio_analysis
            state["status"] = "completed"

            return state

        except Exception as e:
            logger.error(f"Results compilation failed: {e}")
            state["status"] = "failed"
            state["error"] = str(e)
            return state

    def _calculate_overall_score(
        self, risk_metrics: RiskMetrics, factor_analysis: Dict
    ) -> float:
        """Calculate an overall portfolio score (0-100)."""
        try:
            # Base score from risk-adjusted returns
            base_score = 50.0

            # Adjust for Sharpe ratio
            sharpe_adjustment = min(risk_metrics.sharpe_ratio * 10, 20)

            # Adjust for diversification
            diversification_score = factor_analysis.get("diversification_score", 0.5)
            diversification_adjustment = diversification_score * 20

            # Adjust for volatility (lower is better for most investors)
            volatility_adjustment = max(0, 10 - risk_metrics.volatility * 50)

            total_score = (
                base_score
                + sharpe_adjustment
                + diversification_adjustment
                + volatility_adjustment
            )

            return min(max(total_score, 0), 100)  # Clamp between 0 and 100

        except Exception as e:
            logger.warning(f"Score calculation failed: {e}")
            return 50.0  # Default score


# Main analysis function
async def analyze_fund_portfolio(
    portfolio_data: PortfolioSummary, **kwargs
) -> PortfolioAnalysis:
    """
    Main function to analyze a fund portfolio.

    Args:
        portfolio_data: Portfolio summary data
        **kwargs: Additional analysis parameters

    Returns:
        Complete portfolio analysis

    Raises:
        ValueError: If portfolio data is invalid
        Exception: If analysis fails
    """
    try:
        # Initialize workflow
        workflow = FundAdvisoryWorkflow()

        # Prepare initial state
        initial_state = {
            "portfolio_data": portfolio_data,
            "analysis_params": kwargs,
            "status": "started",
            "timestamp": datetime.now().isoformat(),
        }

        # Execute workflow
        logger.info("Starting fund portfolio analysis workflow")
        final_state = await workflow.execute(initial_state)

        # Check for errors
        if final_state.get("status") == "failed":
            error_msg = final_state.get("error", "Unknown error occurred")
            logger.error(f"Workflow failed: {error_msg}")
            raise Exception(f"Portfolio analysis failed: {error_msg}")

        # Extract results
        final_analysis = final_state.get("final_analysis")
        if not final_analysis:
            raise Exception("No analysis results generated")

        logger.info("Fund portfolio analysis completed successfully")
        return final_analysis

    except Exception as e:
        logger.error(f"Fund portfolio analysis failed: {e}")
        raise


# Legacy function for backward compatibility
async def analyze_fund_advisory(
    portfolio_data: PortfolioSummary, **kwargs
) -> PortfolioAnalysis:
    """Legacy function name - redirects to analyze_fund_portfolio."""
    return await analyze_fund_portfolio(portfolio_data, **kwargs)
