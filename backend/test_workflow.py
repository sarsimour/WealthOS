#!/usr/bin/env python3
"""
Test script for the complete WealthOS agent workflow with LangSmith tracing.
"""

import asyncio
import logging
import os
from pathlib import Path

from app.core.config import settings
from app.services.langsmith_service import get_langsmith_service
from app.workflows.fund_advisory import analyze_fund_portfolio
from app.workflows.image_analysis import analyze_portfolio_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_complete_workflow():
    """Test the complete agent workflow from image analysis to fund advisory."""

    print("🚀 Starting WealthOS Agent Workflow Test")
    print("=" * 50)

    # Check LangSmith configuration
    langsmith_service = get_langsmith_service()
    status = "✅ Available" if langsmith_service.is_available() else "❌ Not Available"
    print(f"📊 LangSmith Status: {status}")

    if langsmith_service.is_available():
        print(f"📊 LangSmith Project: {langsmith_service.project_name}")
        tracing_status = (
            "✅ Enabled" if langsmith_service.tracing_enabled else "❌ Disabled"
        )
        print(f"📊 LangSmith Tracing: {tracing_status}")

    print()

    # Test with sample image data (create a simple test image)
    test_image_data = create_test_image_data()

    try:
        print("🖼️  Step 1: Image Analysis")
        print("-" * 30)

        # Analyze the image
        portfolio_summary = await analyze_portfolio_image(
            image_data=test_image_data,
            additional_context=(
                "Analyze this portfolio screenshot to extract fund holdings, values, "
                "and performance data. Please identify all visible fund names, codes, "
                "holding amounts, and any performance metrics shown."
            ),
        )

        print("✅ Image analysis completed!")
        print(f"📊 Holdings extracted: {len(portfolio_summary.holdings)}")
        print(f"💰 Total portfolio value: ¥{portfolio_summary.total_value:,.2f}")

        # Print holdings details
        for i, holding in enumerate(portfolio_summary.holdings, 1):
            print(f"  {i}. {holding.fund_name} ({holding.fund_code})")
            print(f"     Type: {holding.fund_type.value}")
            print(f"     Value: ¥{holding.holding_value:,.2f}")
            if holding.holding_percentage:
                print(f"     Percentage: {holding.holding_percentage:.2f}%")
            print()

        print("🤖 Step 2: Fund Advisory Analysis")
        print("-" * 30)

        # Get fund advisory recommendations
        advisory_result = await analyze_fund_portfolio(
            portfolio_summary=portfolio_summary,
            user_profile={
                "risk_tolerance": "moderate",
                "investment_horizon": "long_term",
                "age": "35",
                "income_level": "high",
            },
        )

        print("✅ Fund advisory analysis completed!")
        print(f"📊 Risk Level: {advisory_result.portfolio_risk.risk_level}")
        print(f"📊 Diversification Score: {advisory_result.diversification_score:.2f}")
        overall_rec = advisory_result.overall_recommendation.recommendation
        print(f"📊 Overall Recommendation: {overall_rec}")

        print("\n🎯 Key Analysis Points:")
        print(
            f"  • Portfolio Volatility: {advisory_result.portfolio_risk.volatility:.2%}"
        )
        print(f"  • Reasoning: {advisory_result.overall_recommendation.reasoning}")

        print("\n🔄 Rebalancing Suggestions:")
        for i, suggestion in enumerate(advisory_result.rebalancing_suggestions, 1):
            print(f"  {i}. {suggestion}")
        print()

        print("🎉 Complete workflow test successful!")

    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        logger.error(f"Workflow test error: {e}", exc_info=True)
        raise


def create_test_image_data() -> bytes:
    """Create test image data for the workflow."""
    # Load the actual portfolio screenshot from data folder
    # Path to the actual screenshot
    screenshot_path = Path(__file__).parent / "data" / "fund_holdings_sample.png"

    try:
        # Read the actual image file
        with open(screenshot_path, "rb") as f:
            image_data = f.read()

        logger.info(f"Loaded actual screenshot: {screenshot_path}")
        logger.info(f"Image size: {len(image_data)} bytes")

        return image_data

    except FileNotFoundError:
        logger.warning(f"Screenshot not found at {screenshot_path}, using dummy data")
        # Fallback to dummy data if file not found
        dummy_image_data = b"DUMMY_PORTFOLIO_IMAGE_DATA" * 100
        return dummy_image_data
    except Exception as e:
        logger.error(f"Error loading screenshot: {e}")
        # Fallback to dummy data on error
        dummy_image_data = b"DUMMY_PORTFOLIO_IMAGE_DATA" * 100
        return dummy_image_data


async def test_langsmith_configuration():
    """Test LangSmith configuration and connectivity."""
    print("🔧 Testing LangSmith Configuration")
    print("-" * 30)

    langsmith_service = get_langsmith_service()

    print(f"API Key configured: {'✅' if settings.LANGSMITH_API_KEY else '❌'}")
    print(f"Project name: {settings.LANGSMITH_PROJECT}")
    print(f"Endpoint: {settings.LANGSMITH_ENDPOINT}")
    print(f"Tracing enabled: {'✅' if settings.LANGSMITH_TRACING else '❌'}")

    if langsmith_service.is_available():
        print("✅ LangSmith service is available and ready")

        # Test creating a run tree
        test_run = langsmith_service.create_run_tree(
            "Test Run", "chain", {"test": "data"}, ["test"]
        )

        if test_run:
            print("✅ Successfully created test run tree")
            test_run.outputs = {"test": "completed"}
            test_run.end()
            print("✅ Successfully logged test run")
        else:
            print("❌ Failed to create test run tree")
    else:
        print("❌ LangSmith service is not available")

    print()


if __name__ == "__main__":
    # Set up environment for testing
    os.environ.setdefault("LANGSMITH_TRACING", "true")

    # Run tests
    asyncio.run(test_langsmith_configuration())
    asyncio.run(test_complete_workflow())
