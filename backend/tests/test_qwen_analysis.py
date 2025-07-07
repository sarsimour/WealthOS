#!/usr/bin/env python3
"""
Test script for Qwen API integration and fund analysis.
"""

import asyncio
import json
import logging
from pathlib import Path

from app.schemas.fund_analysis import PortfolioSummary
from app.services.llm_service import llm_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fund_analysis():
    """Test fund analysis with the Alipay screenshot."""

    # Load the image
    image_path = Path("data/alipay_fund_holdings.jpg")
    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        return

    logger.info(f"Loading image: {image_path}")
    with open(image_path, "rb") as f:
        image_data = f.read()

    logger.info(f"Image size: {len(image_data)} bytes")

    # Create the prompt for fund analysis
    prompt = """
    分析这张支付宝基金持仓截图，提取所有基金的详细信息。
    
    请仔细识别每只基金的：
    1. 基金名称（完整名称）
    2. 基金代码（如果可见）
    3. 持有金额
    4. 基金类型（股票型、债券型、混合型等）
    5. 持有比例（如果可见）
    
    注意：
    - 金额单位可能是元或万元，请正确识别
    - 基金名称要完整准确
    - 如果某些信息不可见，可以设为null
    - 请按照提供的JSON schema格式返回结果
    """

    try:
        logger.info("Starting Qwen API analysis...")

        # Call the LLM service
        result = await llm_service.analyze_image_with_structured_output(
            image_data=image_data,
            prompt=prompt,
            response_model=PortfolioSummary,
            max_tokens=3000,
            temperature=0.1,
        )

        logger.info("✅ Analysis completed successfully!")

        # Print the results
        print("\n" + "=" * 60)
        print("🎯 FUND ANALYSIS RESULTS")
        print("=" * 60)

        print(f"\n📊 Portfolio Summary:")
        print(f"   Total Holdings: {len(result.holdings)}")
        print(f"   Total Value: ¥{result.total_value:,.2f}")
        print(f"   Currency: {result.currency}")
        print(f"   Analysis Date: {result.analysis_date}")

        print(f"\n📈 Individual Holdings:")
        for i, holding in enumerate(result.holdings, 1):
            print(f"\n   {i}. {holding.fund_name}")
            if holding.fund_code:
                print(f"      Code: {holding.fund_code}")
            print(f"      Type: {holding.fund_type}")
            print(f"      Value: ¥{holding.holding_value:,.2f}")
            if holding.holding_percentage is not None:
                print(f"      Portfolio %: {holding.holding_percentage:.2f}%")
            if holding.current_price is not None:
                print(f"      Current Price: ¥{holding.current_price}")

        print(f"\n🔍 Analysis Details:")
        print(f"   Analysis Date: {result.analysis_date}")
        print(f"   Currency: {result.currency}")
        print(f"   Total Holdings: {result.total_holdings}")

        # Convert to JSON for comparison
        result_dict = result.model_dump()

        print(f"\n💾 Raw JSON Output:")
        print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))

        # Compare with expected results (simplified comparison)
        expected_fund_names = [
            "天弘恒生科技指数(QDII)C",
            "华夏恒生互联网科技业ETF联接(QDII)C",
            "广发纳斯达克100ETF联接(QDII)C",
            "大摩沪港深精选混合C",
        ]

        print(f"\n🔄 Fund Detection Check:")
        print("=" * 60)

        detected_fund_names = [h.fund_name for h in result.holdings]

        for expected_name in expected_fund_names:
            found = any(
                expected_name in detected_name for detected_name in detected_fund_names
            )
            print(f"   {'✅' if found else '❌'} {expected_name}")

        print(f"\n📋 All Detected Funds:")
        for name in detected_fund_names:
            print(f"   - {name}")

        print(f"\n🎉 Test completed!")
        return True

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_api_connection():
    """Test basic API connection to Qwen."""

    logger.info("Testing Qwen API connection...")

    try:
        # Simple text generation test
        response = await llm_service.generate_text_response(
            prompt="请说'你好，我是通义千问'", max_tokens=50, temperature=0.1
        )

        logger.info(f"✅ API Connection successful!")
        logger.info(f"Response: {response}")
        return True

    except Exception as e:
        logger.error(f"❌ API Connection failed: {e}")
        return False


async def main():
    """Main test function."""

    print("🚀 Starting Qwen API and Fund Analysis Tests")
    print("=" * 60)

    # Test 1: API Connection
    print("\n1️⃣ Testing API Connection...")
    api_success = await test_api_connection()

    if not api_success:
        print("❌ API connection failed. Please check your API key and base URL.")
        return

    # Test 2: Fund Analysis
    print("\n2️⃣ Testing Fund Analysis...")
    analysis_success = await test_fund_analysis()

    if analysis_success:
        print("\n🎉 All tests passed! Your Qwen integration is working correctly.")
    else:
        print("\n❌ Fund analysis test failed.")


if __name__ == "__main__":
    asyncio.run(main())
