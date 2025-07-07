"""
Tests for fund analysis functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from app.schemas.fund_analysis import (
    FundHolding,
    PortfolioSummary,
    FundType,
    RiskLevel,
    RiskMetrics,
    InvestmentRecommendation,
)


class TestFundAnalysisSchemas:
    """Test fund analysis Pydantic schemas."""

    def test_fund_holding_creation(self):
        """Test creating a fund holding."""
        holding = FundHolding(
            fund_code="000001",
            fund_name="华夏成长混合",
            fund_type=FundType.MIXED,
            holding_value=Decimal("10000.00"),
            holding_percentage=25.0,
            current_price=Decimal("1.2345"),
        )

        assert holding.fund_code == "000001"
        assert holding.fund_name == "华夏成长混合"
        assert holding.fund_type == FundType.MIXED
        assert holding.holding_value == Decimal("10000.00")
        assert holding.holding_percentage == 25.0
        assert holding.current_price == Decimal("1.2345")

    def test_portfolio_summary_creation(self):
        """Test creating a portfolio summary."""
        holdings = [
            FundHolding(
                fund_code="000001",
                fund_name="华夏成长混合",
                fund_type=FundType.MIXED,
                holding_value=Decimal("10000.00"),
                holding_percentage=50.0,
            ),
            FundHolding(
                fund_code="110022",
                fund_name="易方达消费行业股票",
                fund_type=FundType.EQUITY,
                holding_value=Decimal("10000.00"),
                holding_percentage=50.0,
            ),
        ]

        portfolio = PortfolioSummary(
            total_value=Decimal("20000.00"),
            total_holdings=2,
            currency="CNY",
            holdings=holdings,
        )

        assert portfolio.total_value == Decimal("20000.00")
        assert portfolio.total_holdings == 2
        assert portfolio.currency == "CNY"
        assert len(portfolio.holdings) == 2

    def test_risk_metrics_creation(self):
        """Test creating risk metrics."""
        risk = RiskMetrics(
            volatility=0.15,
            sharpe_ratio=1.2,
            max_drawdown=-0.08,
            beta=1.1,
            var_95=-0.05,
            risk_level=RiskLevel.MEDIUM_HIGH,
        )

        assert risk.volatility == 0.15
        assert risk.sharpe_ratio == 1.2
        assert risk.max_drawdown == -0.08
        assert risk.beta == 1.1
        assert risk.var_95 == -0.05
        assert risk.risk_level == RiskLevel.MEDIUM_HIGH

    def test_investment_recommendation_creation(self):
        """Test creating investment recommendation."""
        recommendation = InvestmentRecommendation(
            recommendation="Hold",
            confidence=0.8,
            reasoning="Portfolio is well-balanced with good diversification",
            target_allocation=60.0,
            time_horizon="3-5 years",
            key_risks=["Market volatility", "Interest rate risk"],
            risk_mitigation=["Regular rebalancing", "Diversification"],
        )

        assert recommendation.recommendation == "Hold"
        assert recommendation.confidence == 0.8
        assert (
            recommendation.reasoning
            == "Portfolio is well-balanced with good diversification"
        )
        assert recommendation.target_allocation == 60.0
        assert recommendation.time_horizon == "3-5 years"
        assert len(recommendation.key_risks) == 2
        assert len(recommendation.risk_mitigation) == 2


@pytest.mark.asyncio
class TestImageAnalysisWorkflow:
    """Test image analysis workflow components."""

    @patch("app.workflows.image_analysis.llm_service")
    async def test_image_validation_step(self, mock_llm_service):
        """Test image validation step."""
        from app.workflows.image_analysis import ImageValidationStep
        from app.workflows.base import WorkflowState

        step = ImageValidationStep()

        # Test with valid image data
        state = WorkflowState(
            workflow_id="test",
            context={"image_data": b"fake_image_data"},
            started_at=datetime.now(),
        )

        result = await step.execute(state)
        assert result.context["image_bytes"] == b"fake_image_data"
        assert result.context["image_size"] == len(b"fake_image_data")

    @patch("app.workflows.image_analysis.llm_service")
    async def test_fund_extraction_step(self, mock_llm_service):
        """Test fund extraction step."""
        from app.workflows.image_analysis import FundExtractionStep
        from app.workflows.base import WorkflowState

        # Mock LLM response
        mock_portfolio = PortfolioSummary(
            total_value=Decimal("50000.00"),
            total_holdings=2,
            holdings=[
                FundHolding(
                    fund_code="000001",
                    fund_name="华夏成长混合",
                    fund_type=FundType.MIXED,
                    holding_value=Decimal("30000.00"),
                    holding_percentage=60.0,
                ),
                FundHolding(
                    fund_code="110022",
                    fund_name="易方达消费行业股票",
                    fund_type=FundType.EQUITY,
                    holding_value=Decimal("20000.00"),
                    holding_percentage=40.0,
                ),
            ],
        )

        mock_llm_service.analyze_image_with_structured_output.return_value = (
            mock_portfolio
        )

        step = FundExtractionStep()
        state = WorkflowState(
            workflow_id="test",
            context={"image_bytes": b"fake_image_data"},
            started_at=datetime.now(),
        )

        result = await step.execute(state)
        assert "portfolio_summary" in result.context
        assert result.context["holdings_count"] == 2


@pytest.mark.asyncio
class TestFundAdvisoryWorkflow:
    """Test fund advisory workflow components."""

    async def test_portfolio_validation_step(self):
        """Test portfolio validation step."""
        from app.workflows.fund_advisory import PortfolioValidationStep
        from app.workflows.base import WorkflowState

        portfolio = PortfolioSummary(
            total_value=Decimal("50000.00"),
            total_holdings=2,
            holdings=[
                FundHolding(
                    fund_code="000001",
                    fund_name="华夏成长混合",
                    fund_type=FundType.MIXED,
                    holding_value=Decimal("30000.00"),
                    holding_percentage=60.0,
                ),
                FundHolding(
                    fund_code="110022",
                    fund_name="易方达消费行业股票",
                    fund_type=FundType.EQUITY,
                    holding_value=Decimal("20000.00"),
                    holding_percentage=40.0,
                ),
            ],
        )

        step = PortfolioValidationStep()
        state = WorkflowState(
            workflow_id="test",
            context={"portfolio_summary": portfolio},
            started_at=datetime.now(),
        )

        result = await step.execute(state)
        assert result.context["portfolio_summary"] == portfolio

    async def test_risk_analysis_step(self):
        """Test risk analysis step."""
        from app.workflows.fund_advisory import RiskAnalysisStep
        from app.workflows.base import WorkflowState

        portfolio = PortfolioSummary(
            total_value=Decimal("50000.00"),
            total_holdings=2,
            holdings=[
                FundHolding(
                    fund_code="000001",
                    fund_name="华夏成长混合",
                    fund_type=FundType.MIXED,
                    holding_value=Decimal("30000.00"),
                    holding_percentage=60.0,
                ),
                FundHolding(
                    fund_code="110022",
                    fund_name="易方达消费行业股票",
                    fund_type=FundType.EQUITY,
                    holding_value=Decimal("20000.00"),
                    holding_percentage=40.0,
                ),
            ],
        )

        step = RiskAnalysisStep()
        state = WorkflowState(
            workflow_id="test",
            context={"portfolio_summary": portfolio},
            started_at=datetime.now(),
        )

        result = await step.execute(state)
        assert "portfolio_risk" in result.context
        assert "diversification_score" in result.context

        portfolio_risk = result.context["portfolio_risk"]
        assert isinstance(portfolio_risk, RiskMetrics)
        assert portfolio_risk.volatility > 0

        diversification_score = result.context["diversification_score"]
        assert 0.0 <= diversification_score <= 1.0


@pytest.mark.asyncio
class TestAPIEndpoints:
    """Test API endpoint functionality."""

    @patch("app.api.v1.fund_analysis.analyze_portfolio_image")
    async def test_upload_portfolio_image_endpoint(self, mock_analyze):
        """Test the upload portfolio image endpoint."""
        from fastapi.testclient import TestClient
        from app.main import app

        # Mock the analysis result
        mock_portfolio = PortfolioSummary(
            total_value=Decimal("50000.00"),
            total_holdings=1,
            holdings=[
                FundHolding(
                    fund_code="000001",
                    fund_name="华夏成长混合",
                    fund_type=FundType.MIXED,
                    holding_value=Decimal("50000.00"),
                    holding_percentage=100.0,
                )
            ],
        )
        mock_analyze.return_value = mock_portfolio

        client = TestClient(app)

        # Create a fake image file
        fake_image = b"fake_image_data"

        response = client.post(
            "/api/v1/fund-analysis/upload-image",
            files={"file": ("test.png", fake_image, "image/png")},
            data={"additional_context": "Test portfolio"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["portfolio_summary"]["total_holdings"] == 1
