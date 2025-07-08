"""
Image Analysis Workflow

LangGraph workflow for analyzing fund portfolio screenshots and extracting holdings.
"""

import base64
import logging
import time
from datetime import datetime
from typing import Optional

from app.schemas.fund_analysis import FundHolding, FundType, PortfolioSummary
from app.services.llm_service import llm_service
from app.services.langsmith_service import get_langsmith_service
from app.workflows.base import BaseWorkflow, WorkflowState, WorkflowStep

logger = logging.getLogger(__name__)


class ImageValidationStep(WorkflowStep):
    """Validate uploaded image data."""

    def __init__(self):
        super().__init__(
            name="image_validation",
            description="Validate and preprocess uploaded image data",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Validate image data in the workflow context."""
        langsmith_service = get_langsmith_service()
        validation_run = None

        if state.context.get("run_tree"):
            validation_run = langsmith_service.create_child_run(
                state.context["run_tree"],
                "Image Validation",
                "tool",
                {"step": "image_validation"},
                ["validation", "preprocessing"],
            )

        try:
            # Get image data from context
            image_data = state.context.get("image_data")
            if not image_data:
                raise ValueError("No image data provided")

            # If it's base64 encoded, decode it
            if isinstance(image_data, str):
                try:
                    decoded_data = base64.b64decode(image_data)
                    state.context["image_bytes"] = decoded_data
                except Exception as e:
                    raise ValueError(f"Invalid base64 image data: {e}")
            else:
                state.context["image_bytes"] = image_data

            # Validate image size (max 10MB)
            image_size = len(state.context["image_bytes"])
            if image_size > 10 * 1024 * 1024:
                raise ValueError("Image size exceeds 10MB limit")

            # Validate minimum size (at least 1KB)
            if image_size < 1024:
                raise ValueError("Image size too small, minimum 1KB required")

            state.context["image_size"] = image_size
            self.logger.info(f"Image validated: {image_size} bytes")

            # Log validation results to LangSmith
            if validation_run:
                validation_run.outputs = {
                    "image_size": image_size,
                    "validation_status": "success",
                }
                validation_run.end()

            return state

        except Exception as e:
            self.logger.error(f"Image validation failed: {e}")
            if validation_run:
                validation_run.outputs = {
                    "error": str(e),
                    "validation_status": "failed",
                }
                validation_run.end()
            raise


class FundExtractionStep(WorkflowStep):
    """Extract fund holdings from image using GPT-4 Vision."""

    def __init__(self):
        super().__init__(
            name="fund_extraction",
            description="Extract fund holdings data from portfolio screenshot",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Extract fund holdings using LLM vision analysis."""
        langsmith_service = get_langsmith_service()
        extraction_run = None

        if state.context.get("run_tree"):
            extraction_run = langsmith_service.create_child_run(
                state.context["run_tree"],
                "Fund Extraction",
                "llm",
                {"step": "fund_extraction"},
                ["llm", "vision", "extraction"],
            )

        try:
            image_bytes = state.context.get("image_bytes")
            if not image_bytes:
                raise ValueError("No image data available for analysis")

            # Prepare the analysis prompt
            prompt = """
            Analyze this portfolio screenshot and extract all fund holdings information.
            
            Please identify and extract:
            1. Fund codes/tickers (like 000001, 110003, etc.)
            2. Fund names (full Chinese names)
            3. Fund types (equity, bond, mixed, etc.)
            4. Current holding values (in CNY)
            5. Holding percentages if visible
            6. Current prices if visible
            7. Total portfolio value
            
            Important guidelines:
            - Extract data exactly as shown in the image
            - If information is not clearly visible, mark as null
            - Convert all monetary values to CNY
            - Classify fund types based on names and codes
            - Calculate percentages if total value is available
            
            Return structured data with all identified holdings.
            """

            # Log LLM call to LangSmith
            if extraction_run:
                langsmith_service.log_llm_call(
                    extraction_run,
                    "qwen-vl-max",
                    prompt,
                    "Processing image...",
                    {"image_size": len(image_bytes)},
                )

            # Use LLM service to analyze the image
            portfolio_summary = await llm_service.analyze_image_with_structured_output(
                image_data=image_bytes,
                prompt=prompt,
                response_model=PortfolioSummary,
                max_tokens=3000,
                temperature=0.1,
            )

            # Store results in context
            state.context["portfolio_summary"] = portfolio_summary
            state.context["holdings_count"] = len(portfolio_summary.holdings)

            self.logger.info(
                f"Extracted {len(portfolio_summary.holdings)} fund holdings"
            )

            # Log extraction results to LangSmith
            if extraction_run:
                extraction_run.outputs = {
                    "holdings_count": len(portfolio_summary.holdings),
                    "total_value": portfolio_summary.total_value,
                    "extraction_status": "success",
                }
                extraction_run.end()

            return state

        except Exception as e:
            self.logger.error(f"Fund extraction failed: {e}")
            if extraction_run:
                extraction_run.outputs = {
                    "error": str(e),
                    "extraction_status": "failed",
                }
                extraction_run.end()
            raise


class DataEnrichmentStep(WorkflowStep):
    """Enrich extracted fund data with additional information."""

    def __init__(self):
        super().__init__(
            name="data_enrichment",
            description="Enrich fund data with market information and classifications",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Enrich fund data with additional market information."""
        try:
            portfolio_summary = state.context.get("portfolio_summary")
            if not portfolio_summary:
                raise ValueError("No portfolio summary available for enrichment")

            # TODO: Implement data enrichment with akshare
            # For now, we'll enhance the basic classification

            enriched_holdings = []
            for holding in portfolio_summary.holdings:
                # Enhance fund type classification based on code patterns
                enhanced_holding = self._enhance_fund_classification(holding)
                enriched_holdings.append(enhanced_holding)

            # Update portfolio summary with enriched data
            portfolio_summary.holdings = enriched_holdings
            state.context["portfolio_summary"] = portfolio_summary

            self.logger.info("Fund data enrichment completed")

            return state

        except Exception as e:
            self.logger.error(f"Data enrichment failed: {e}")
            raise

    def _enhance_fund_classification(self, holding: FundHolding) -> FundHolding:
        """Enhance fund type classification based on code patterns."""
        fund_code = holding.fund_code
        fund_name = holding.fund_name.lower()

        # Chinese fund code patterns
        if fund_code.startswith(
            ("000", "001", "002", "003", "004", "005", "006", "007", "008", "009")
        ):
            # Mutual fund codes
            if any(
                keyword in fund_name for keyword in ["股票", "权益", "成长", "价值"]
            ):
                holding.fund_type = FundType.EQUITY
            elif any(keyword in fund_name for keyword in ["债券", "债", "固收"]):
                holding.fund_type = FundType.BOND
            elif any(keyword in fund_name for keyword in ["混合", "配置", "平衡"]):
                holding.fund_type = FundType.MIXED
            elif any(keyword in fund_name for keyword in ["货币", "现金", "流动"]):
                holding.fund_type = FundType.MONEY_MARKET

        elif fund_code.startswith(("1", "5")):
            # ETF codes
            holding.fund_type = FundType.EQUITY

        return holding


class ResultValidationStep(WorkflowStep):
    """Validate and finalize extraction results."""

    def __init__(self):
        super().__init__(
            name="result_validation",
            description="Validate extraction results and prepare final output",
        )

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Validate and finalize the extraction results."""
        try:
            portfolio_summary = state.context.get("portfolio_summary")
            if not portfolio_summary:
                raise ValueError("No portfolio summary available for validation")

            # Validate portfolio summary
            if not portfolio_summary.holdings:
                raise ValueError("No fund holdings extracted from image")

            # Validate individual holdings
            for holding in portfolio_summary.holdings:
                if not holding.fund_code or not holding.fund_name:
                    self.logger.warning(f"Incomplete holding data: {holding}")

                if holding.holding_value <= 0:
                    self.logger.warning(
                        f"Invalid holding value: {holding.holding_value}"
                    )

            # Calculate percentages if not provided
            if portfolio_summary.total_value > 0:
                for holding in portfolio_summary.holdings:
                    if holding.holding_percentage is None:
                        holding.holding_percentage = float(
                            (holding.holding_value / portfolio_summary.total_value)
                            * 100
                        )

            # Store final results
            state.context["final_results"] = portfolio_summary
            state.context["extraction_success"] = True

            self.logger.info("Result validation completed successfully")

            return state

        except Exception as e:
            self.logger.error(f"Result validation failed: {e}")
            state.context["extraction_success"] = False
            raise


class ImageAnalysisWorkflow(BaseWorkflow):
    """Complete workflow for analyzing fund portfolio images."""

    def __init__(self):
        super().__init__(
            name="image_analysis",
            description="Analyze fund portfolio screenshots and extract holdings",
        )

        # Add workflow steps
        self.add_step(ImageValidationStep())
        self.add_step(FundExtractionStep())
        self.add_step(DataEnrichmentStep())
        self.add_step(ResultValidationStep())

        self.logger.info("Image analysis workflow initialized")

    async def analyze_image(
        self, image_data: bytes, additional_context: Optional[str] = None
    ) -> PortfolioSummary:
        """Analyze an image and return portfolio summary."""
        try:
            # Create LangSmith run tree for tracing
            langsmith_service = get_langsmith_service()
            run_tree = langsmith_service.create_run_tree(
                "Image Analysis Workflow",
                "chain",
                {
                    "image_size": len(image_data),
                    "additional_context": additional_context,
                },
                ["workflow", "image_analysis", "fund_extraction"],
            )

            # Create initial state with image data
            initial_state = WorkflowState(
                workflow_id=f"img_analysis_{int(time.time())}",
                started_at=datetime.now(),
                context={
                    "image_data": image_data,
                    "additional_context": additional_context,
                    "run_tree": run_tree,  # Pass run_tree to workflow steps
                },
            )

            # Execute the workflow
            result_state = await self.execute(initial_state)

            if result_state.status == "error":
                # Log error to LangSmith
                if run_tree:
                    run_tree.outputs = {
                        "error": result_state.error_message,
                        "status": "failed",
                    }
                    run_tree.end()
                raise ValueError(f"Workflow failed: {result_state.error_message}")

            # Extract final results
            portfolio_summary = result_state.context.get("final_results")
            if not portfolio_summary:
                if run_tree:
                    run_tree.outputs = {
                        "error": "No results produced by workflow",
                        "status": "failed",
                    }
                    run_tree.end()
                raise ValueError("No results produced by workflow")

            # Log success to LangSmith
            if run_tree:
                run_tree.outputs = {
                    "holdings_count": len(portfolio_summary.holdings),
                    "total_value": portfolio_summary.total_value,
                    "status": "success",
                }
                run_tree.end()

            return portfolio_summary

        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            raise


# Create workflow instance
image_analysis_workflow = ImageAnalysisWorkflow()


# Helper function for direct usage
async def analyze_portfolio_image(
    image_data: bytes, additional_context: Optional[str] = None
) -> PortfolioSummary:
    """Analyze a portfolio image and return extracted holdings."""
    return await image_analysis_workflow.analyze_image(image_data, additional_context)
