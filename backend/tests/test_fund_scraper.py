"""
Test script for the fund holdings scraper.

This script tests the scraper with a few sample funds to verify it works correctly.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

try:
    from app.data.fund_holdings_scraper import FundHoldingsScraper
except ImportError as e:
    print(f"Error importing fund_holdings_scraper: {e}")
    print(
        "Please ensure all dependencies are installed: uv add aiohttp beautifulsoup4 lxml"
    )
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_scraper():
    """Test the fund holdings scraper with sample funds."""

    # Create output directory
    output_dir = "test_scraper_output"
    Path(output_dir).mkdir(exist_ok=True)

    # Initialize scraper
    scraper = FundHoldingsScraper(output_dir)

    # Test with some well-known Chinese funds
    test_funds = [
        "000001",  # 华夏成长混合
        "000002",  # 华夏回报混合
        "000003",  # 中海可转债债券A
        "000300",  # 中银中证100指数
        "001000",  # 中欧瑞丰灵活配置混合
    ]

    logger.info(f"Testing fund holdings scraper with {len(test_funds)} funds")
    logger.info(f"Output directory: {output_dir}")

    successful = []
    failed = []

    for fund_code in test_funds:
        logger.info(f"Testing fund {fund_code}...")

        try:
            csv_path = await scraper.scrape_single_fund(fund_code)

            if csv_path and os.path.exists(csv_path):
                # Verify the CSV has data
                import pandas as pd

                df = pd.read_csv(csv_path)
                logger.info(
                    f"✅ Fund {fund_code}: {len(df)} holdings saved to {csv_path}"
                )
                successful.append(fund_code)

                # Show a sample of the data
                if len(df) > 0:
                    logger.info(f"Sample data for {fund_code}:")
                    logger.info(f"Columns: {list(df.columns)}")
                    logger.info(f"First few rows:\n{df.head(3).to_string()}")

            else:
                logger.error(f"❌ Fund {fund_code}: No data scraped")
                failed.append(fund_code)

        except Exception as e:
            logger.error(f"❌ Fund {fund_code}: Error - {e}")
            failed.append(fund_code)

        # Wait between requests to be respectful
        await asyncio.sleep(3)

    # Summary
    logger.info("=== TEST RESULTS ===")
    logger.info(f"Total funds tested: {len(test_funds)}")
    logger.info(f"Successful: {len(successful)} - {successful}")
    logger.info(f"Failed: {len(failed)} - {failed}")
    logger.info(f"Success rate: {len(successful)/len(test_funds)*100:.1f}%")

    # List output files
    output_files = list(Path(output_dir).glob("*.csv"))
    logger.info(f"CSV files created: {len(output_files)}")
    for file in output_files:
        size_mb = file.stat().st_size / 1024 / 1024
        logger.info(f"  {file.name}: {size_mb:.2f} MB")


if __name__ == "__main__":
    asyncio.run(test_scraper())
