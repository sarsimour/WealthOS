import random
import time
from typing import Dict, Any
from app.services.protocols import PriceProvider


class MockProvider(PriceProvider):
    """Mock price provider for testing purposes."""

    def __init__(self):
        self.base_price = 45000.0  # Base Bitcoin price
        self.last_price = self.base_price
        self.last_update = time.time()

    async def get_price(self, base_asset: str, quote_currency: str) -> float:
        """Return mock price data with realistic variation."""
        current_time = time.time()

        # Simulate price movement every 5 seconds
        if current_time - self.last_update > 5:
            # Random walk with small changes
            change_percent = random.uniform(-0.02, 0.02)  # ±2% change
            self.last_price *= 1 + change_percent

            # Keep price in reasonable range
            if self.last_price < 40000:
                self.last_price = 40000
            elif self.last_price > 50000:
                self.last_price = 50000

            self.last_update = current_time

        return round(self.last_price, 2)

    async def get_historical_prices(
        self, base_asset: str, quote_currency: str, days: int = 1
    ) -> Dict[str, Any]:
        """Return mock historical price data."""
        current_price = await self.get_price(base_asset, quote_currency)

        # Generate 24 hours of mock data (hourly)
        historical_data = []
        for i in range(24):
            # Each hour, small random variation
            variation = random.uniform(-0.01, 0.01)  # ±1% per hour
            price = current_price * (1 + variation * (24 - i) / 24)
            timestamp = int(time.time()) - (i * 3600)  # i hours ago

            historical_data.append({"timestamp": timestamp, "price": round(price, 2)})

        # Reverse to get chronological order
        historical_data.reverse()

        return {
            "symbol": f"{base_asset}{quote_currency}",
            "current_price": current_price,
            "price_change_24h": round(current_price - historical_data[0]["price"], 2),
            "price_change_percent_24h": round(
                (
                    (current_price - historical_data[0]["price"])
                    / historical_data[0]["price"]
                )
                * 100,
                2,
            ),
            "high_24h": round(max(data["price"] for data in historical_data), 2),
            "low_24h": round(min(data["price"] for data in historical_data), 2),
            "historical_data": historical_data,
        }
