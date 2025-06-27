#!/usr/bin/env python3
"""
Integration test for BTC price history functionality
Tests backend endpoint and verifies data structure
"""

import asyncio
import json
import requests
from datetime import datetime

BACKEND_URL = "http://localhost:8001"


def test_backend_endpoints():
    """Test the backend endpoints for BTC price history"""
    print("🧪 Testing BTC Price History Integration")
    print("=" * 50)

    # Test endpoints
    endpoints_to_test = [
        {
            "name": "Current Bitcoin Price",
            "url": f"{BACKEND_URL}/api/v1/prices/crypto/btc",
            "params": {"vs_currency": "usd"},
        },
        {
            "name": "Bitcoin Full Data (1 day)",
            "url": f"{BACKEND_URL}/api/v1/prices/bitcoin/full",
            "params": {"days": 1},
        },
        {
            "name": "Bitcoin History (1 day)",
            "url": f"{BACKEND_URL}/api/v1/prices/bitcoin/history",
            "params": {"period": "1d"},
        },
        {
            "name": "Bitcoin History (7 days)",
            "url": f"{BACKEND_URL}/api/v1/prices/bitcoin/history",
            "params": {"period": "7d"},
        },
        {
            "name": "Bitcoin History (30 days)",
            "url": f"{BACKEND_URL}/api/v1/prices/bitcoin/history",
            "params": {"period": "30d"},
        },
    ]

    results = []

    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing: {endpoint['name']}")
        try:
            response = requests.get(
                endpoint["url"], params=endpoint.get("params", {}), timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Validate response structure based on endpoint
                if "bitcoin/history" in endpoint["url"]:
                    validate_historical_response(data, endpoint["name"])
                elif "bitcoin/full" in endpoint["url"]:
                    validate_full_response(data, endpoint["name"])
                elif "crypto/btc" in endpoint["url"]:
                    validate_price_response(data, endpoint["name"])

                results.append(
                    {
                        "endpoint": endpoint["name"],
                        "status": "✅ PASS",
                        "data_points": (
                            len(data.get("data", [])) if "data" in data else "N/A"
                        ),
                        "response_time": f"{response.elapsed.total_seconds():.2f}s",
                    }
                )
                print(f"   ✅ Success: {response.status_code}")
                print(f"   ⏱️  Response time: {response.elapsed.total_seconds():.2f}s")

            else:
                results.append(
                    {
                        "endpoint": endpoint["name"],
                        "status": f"❌ FAIL ({response.status_code})",
                        "data_points": "N/A",
                        "response_time": f"{response.elapsed.total_seconds():.2f}s",
                    }
                )
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")

        except requests.exceptions.RequestException as e:
            results.append(
                {
                    "endpoint": endpoint["name"],
                    "status": f"❌ ERROR",
                    "data_points": "N/A",
                    "response_time": "N/A",
                }
            )
            print(f"   ❌ Error: {str(e)}")

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    for result in results:
        print(f"{result['status']} {result['endpoint']}")
        print(f"   📈 Data points: {result['data_points']}")
        print(f"   ⏱️  Response time: {result['response_time']}")
        print()

    # Overall status
    passed = sum(1 for r in results if "✅" in r["status"])
    total = len(results)

    print(f"📋 Overall: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 All tests passed! BTC price history functionality is working correctly."
        )
        return True
    else:
        print("⚠️  Some tests failed. Check the backend server and dependencies.")
        return False


def validate_historical_response(data, endpoint_name):
    """Validate historical data response structure"""
    required_fields = ["symbol", "currency", "period", "interval", "data", "metadata"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' in {endpoint_name}")

    # Validate data points
    if not isinstance(data["data"], list):
        raise ValueError(f"Data field should be a list in {endpoint_name}")

    if len(data["data"]) > 0:
        # Check first data point structure
        point = data["data"][0]
        if not all(key in point for key in ["timestamp", "price"]):
            raise ValueError(f"Invalid data point structure in {endpoint_name}")

    # Validate metadata
    metadata = data["metadata"]
    required_meta_fields = ["total_points", "start_time", "end_time", "interval"]
    for field in required_meta_fields:
        if field not in metadata:
            raise ValueError(f"Missing metadata field '{field}' in {endpoint_name}")

    print(f"   📊 Data validation: ✅ ({len(data['data'])} points)")


def validate_full_response(data, endpoint_name):
    """Validate full Bitcoin data response structure"""
    required_fields = [
        "symbol",
        "current_price",
        "price_change_24h",
        "price_change_percent_24h",
        "high_24h",
        "low_24h",
        "historical_data",
        "currency",
        "last_updated",
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' in {endpoint_name}")

    # Validate historical data
    if not isinstance(data["historical_data"], list):
        raise ValueError(f"Historical data should be a list in {endpoint_name}")

    print(f"   📊 Data validation: ✅ (Current: ${data['current_price']:.2f})")


def validate_price_response(data, endpoint_name):
    """Validate price response structure"""
    required_fields = ["identifier", "currency", "price"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' in {endpoint_name}")

    print(f"   📊 Data validation: ✅ (Price: ${data['price']:.2f})")


def test_frontend_urls():
    """Test if frontend URLs are accessible"""
    print("\n🌐 Testing Frontend URLs")
    print("=" * 50)

    frontend_url = "http://localhost:5173"  # Vite default port

    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {str(e)}")
        print("💡 Make sure to run: cd frontend && pnpm dev")
        return False


if __name__ == "__main__":
    print("🚀 Starting BTC Price History Integration Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test backend
    backend_success = test_backend_endpoints()

    # Test frontend
    frontend_success = test_frontend_urls()

    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS")
    print("=" * 50)

    if backend_success and frontend_success:
        print("🎉 ALL SYSTEMS GO! BTC price history functionality is fully working.")
        print("\n📋 Next steps:")
        print("   1. Open http://localhost:5173 to see the frontend")
        print("   2. Check the Bitcoin chart with different timeframes")
        print("   3. Verify real-time price updates")
    elif backend_success:
        print("✅ Backend is working correctly")
        print("⚠️  Frontend needs attention")
    else:
        print("❌ Backend issues detected")
        print("\n🔧 Troubleshooting:")
        print(
            "   1. Make sure backend is running: cd backend && python -m uvicorn app.main:app --reload"
        )
        print("   2. Check if all dependencies are installed: cd backend && uv sync")
        print("   3. Verify database connections and API keys")

    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
