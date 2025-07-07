"""
Fund Analysis Schemas

Pydantic models for fund holdings extraction, analysis, and API responses.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class FundType(str, Enum):
    """Fund type classification."""

    EQUITY = "equity"
    BOND = "bond"
    MIXED = "mixed"
    MONEY_MARKET = "money_market"
    COMMODITY = "commodity"
    ALTERNATIVE = "alternative"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "low"
    MEDIUM_LOW = "medium_low"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"


class FundHolding(BaseModel):
    """Individual fund holding extracted from screenshot."""

    fund_code: str = Field(..., description="Fund code/ticker")
    fund_name: str = Field(..., description="Fund name")
    fund_type: FundType = Field(..., description="Type of fund")
    holding_value: Decimal = Field(..., description="Current holding value")
    holding_percentage: Optional[float] = Field(
        None, description="Percentage of total portfolio"
    )
    purchase_date: Optional[datetime] = Field(
        None, description="Purchase date if available"
    )
    current_price: Optional[Decimal] = Field(None, description="Current unit price")

    @field_validator("holding_percentage")
    @classmethod
    def validate_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Percentage must be between 0 and 100")
        return v


class PortfolioSummary(BaseModel):
    """Portfolio summary from screenshot analysis."""

    total_value: Decimal = Field(..., description="Total portfolio value")
    total_holdings: int = Field(..., description="Number of holdings")
    currency: str = Field(default="CNY", description="Portfolio currency")
    analysis_date: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp"
    )
    holdings: List[FundHolding] = Field(..., description="List of fund holdings")


class RiskMetrics(BaseModel):
    """Risk analysis metrics for a fund or portfolio."""

    volatility: float = Field(..., description="Annualized volatility")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown")
    beta: Optional[float] = Field(None, description="Beta coefficient")
    var_95: Optional[float] = Field(None, description="95% Value at Risk")
    risk_level: RiskLevel = Field(..., description="Overall risk classification")


class FundAnalysis(BaseModel):
    """Comprehensive fund analysis result."""

    fund_code: str = Field(..., description="Fund code")
    fund_name: str = Field(..., description="Fund name")
    fund_type: FundType = Field(..., description="Fund type")

    # Performance metrics
    current_price: Decimal = Field(..., description="Current unit price")
    ytd_return: Optional[float] = Field(None, description="Year-to-date return")
    one_year_return: Optional[float] = Field(None, description="1-year return")
    three_year_return: Optional[float] = Field(
        None, description="3-year annualized return"
    )

    # Risk metrics
    risk_metrics: RiskMetrics = Field(..., description="Risk analysis")

    # Additional info
    fund_manager: Optional[str] = Field(None, description="Fund manager")
    management_fee: Optional[float] = Field(None, description="Annual management fee")
    aum: Optional[Decimal] = Field(None, description="Assets under management")

    # Analysis metadata
    analysis_date: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp"
    )
    data_source: str = Field(default="akshare", description="Data source")


class InvestmentRecommendation(BaseModel):
    """Investment recommendation for a fund or portfolio."""

    recommendation: str = Field(..., description="Buy/Hold/Sell recommendation")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Detailed reasoning")
    target_allocation: Optional[float] = Field(
        None, description="Recommended allocation percentage"
    )
    time_horizon: Optional[str] = Field(None, description="Recommended holding period")

    # Risk considerations
    key_risks: List[str] = Field(default_factory=list, description="Key risk factors")
    risk_mitigation: List[str] = Field(
        default_factory=list, description="Risk mitigation strategies"
    )


class PortfolioAnalysis(BaseModel):
    """Complete portfolio analysis result."""

    portfolio_summary: PortfolioSummary = Field(..., description="Portfolio overview")
    fund_analyses: List[FundAnalysis] = Field(
        ..., description="Individual fund analyses"
    )

    # Portfolio-level metrics
    portfolio_risk: RiskMetrics = Field(..., description="Portfolio risk metrics")
    diversification_score: float = Field(..., description="Diversification score (0-1)")

    # Asset allocation
    asset_allocation: Dict[str, float] = Field(
        ..., description="Asset allocation breakdown"
    )
    sector_allocation: Dict[str, float] = Field(
        default_factory=dict, description="Sector allocation"
    )
    geographic_allocation: Dict[str, float] = Field(
        default_factory=dict, description="Geographic allocation"
    )

    # Recommendations
    overall_recommendation: InvestmentRecommendation = Field(
        ..., description="Overall portfolio recommendation"
    )
    rebalancing_suggestions: List[str] = Field(
        default_factory=list, description="Rebalancing suggestions"
    )

    # Analysis metadata
    analysis_date: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp"
    )


# API Request/Response Models


class ImageAnalysisRequest(BaseModel):
    """Request for image analysis."""

    image_data: str = Field(..., description="Base64 encoded image data")
    analysis_type: str = Field(default="fund_holdings", description="Type of analysis")
    additional_context: Optional[str] = Field(
        None, description="Additional context or instructions"
    )


class ImageAnalysisResponse(BaseModel):
    """Response from image analysis."""

    success: bool = Field(..., description="Analysis success status")
    portfolio_summary: Optional[PortfolioSummary] = Field(
        None, description="Extracted portfolio data"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )


class FundAdvisoryRequest(BaseModel):
    """Request for fund investment advisory."""

    portfolio_summary: PortfolioSummary = Field(..., description="Portfolio to analyze")
    user_profile: Optional[Dict[str, str]] = Field(
        None, description="User risk profile and preferences"
    )
    advisory_type: str = Field(default="comprehensive", description="Type of advisory")


class FundAdvisoryResponse(BaseModel):
    """Response from fund advisory analysis."""

    success: bool = Field(..., description="Analysis success status")
    portfolio_analysis: Optional[PortfolioAnalysis] = Field(
        None, description="Complete portfolio analysis"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )


class WorkflowStatus(BaseModel):
    """Workflow execution status."""

    workflow_id: str = Field(..., description="Workflow execution ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., description="Progress percentage (0-100)")
    current_step: str = Field(..., description="Current workflow step")
    started_at: datetime = Field(..., description="Workflow start time")
    completed_at: Optional[datetime] = Field(
        None, description="Workflow completion time"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")


# Additional API models for simplified endpoints
class AdvisoryRequest(BaseModel):
    """Simplified advisory request."""

    portfolio_summary: PortfolioSummary
    user_profile: Optional[Dict[str, str]] = None


class AdvisoryResponse(BaseModel):
    """Simplified advisory response."""

    success: bool
    portfolio_analysis: Optional[PortfolioAnalysis] = None
    message: str
    processing_time: Optional[float] = None
    error_details: Optional[str] = None
