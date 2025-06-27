#!/usr/bin/env python3
"""
Simple mock API server for testing frontend without backend dependencies.
This helps isolate CORS and frontend issues.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Mock Bitcoin API", version="1.0.0")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be permissive for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_mock_bitcoin_price() -> float:
    """Generate a realistic mock Bitcoin price."""
    base_price = 42000
    variation = random.uniform(-2000, 2000)
    return round(base_price + variation, 2)


def generate_mock_history(days: int = 1) -> List[Dict[str, Any]]:
    """Generate mock historical Bitcoin data."""
    data = []
    current_time = datetime.now()
    current_price = generate_mock_bitcoin_price()

    # Generate data points every 15 minutes for the last X days
    points_per_day = 96  # 24 hours * 4 (every 15 minutes)
    total_points = days * points_per_day

    for i in range(total_points):
        timestamp = current_time - timedelta(minutes=15 * (total_points - i))

        # Add some realistic price movement
        price_change = random.uniform(-500, 500)
        current_price = max(35000, min(50000, current_price + price_change))

        data.append(
            {
                "timestamp": timestamp.isoformat(),
                "price": round(current_price, 2),
                "volume": random.uniform(100, 1000),
            }
        )

    return data


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/v1/prices/crypto/btc")
async def get_bitcoin_current_price():
    """Mock current Bitcoin price endpoint."""
    price = generate_mock_bitcoin_price()
    return {
        "symbol": "btc",
        "price": price,
        "currency": "usd",
        "timestamp": datetime.now().isoformat(),
        "source": "mock",
        "change_24h": random.uniform(-5, 5),
        "change_24h_percent": random.uniform(-10, 10),
    }


@app.get("/api/v1/prices/bitcoin/history")
async def get_bitcoin_history(period: str = "1d"):
    """Mock Bitcoin history endpoint."""
    period_days = {"1d": 1, "7d": 7, "30d": 30, "1y": 365}

    days = period_days.get(period, 1)
    data = generate_mock_history(days)

    return {
        "symbol": "bitcoin",
        "currency": "usd",
        "period": period,
        "count": len(data),
        "data": data,
        "source": "mock",
    }


@app.get("/api/v1/prices/bitcoin/full")
async def get_bitcoin_full_data(days: int = 1):
    """Mock Bitcoin full data endpoint."""
    data = generate_mock_history(days)
    current = generate_mock_bitcoin_price()

    return {
        "current_price": current,
        "historical_data": data,
        "period_days": days,
        "currency": "usd",
        "source": "mock",
        "metadata": {
            "total_points": len(data),
            "first_timestamp": data[0]["timestamp"] if data else None,
            "last_timestamp": data[-1]["timestamp"] if data else None,
            "generated_at": datetime.now().isoformat(),
        },
    }


@app.get("/api/v1/cache/stats")
async def get_cache_stats():
    """Mock cache stats endpoint."""
    return {
        "status": "mock",
        "redis_available": False,
        "cache_hits": random.randint(50, 200),
        "cache_misses": random.randint(10, 50),
        "cache_entries": random.randint(5, 20),
    }


if __name__ == "__main__":
    print("🚀 Starting Mock Bitcoin API Server...")
    print("📊 This server provides fake Bitcoin data for frontend testing")
    print("🌐 CORS is enabled for all origins")
    print("💡 Use this to test frontend without backend dependencies")
    print("")
    print("Available endpoints:")
    print("  GET /health - Health check")
    print("  GET /api/v1/prices/crypto/btc - Current Bitcoin price")
    print("  GET /api/v1/prices/bitcoin/history?period=1d - Historical data")
    print("  GET /api/v1/prices/bitcoin/full?days=1 - Full Bitcoin data")
    print("  GET /api/v1/cache/stats - Cache statistics")
    print("")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,  # Different port to avoid conflicts
        log_level="info",
    )
