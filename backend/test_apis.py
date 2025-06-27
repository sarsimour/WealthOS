#!/usr/bin/env python3
"""
Test script to verify both real backend and mock API servers are working.
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def test_endpoint(session, url, name):
    """Test a single endpoint."""
    try:
        print(f"🧪 Testing {name}: {url}")
        async with session.get(url) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                print(f"   ✅ SUCCESS: {status} - {len(str(data))} bytes")
                return True
            else:
                print(f"   ❌ FAILED: {status}")
                return False
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        return False


async def main():
    """Test both APIs."""
    print("🚀 API Testing Suite")
    print("=" * 50)

    # Test endpoints
    test_cases = [
        # Real Backend (port 8001)
        ("http://127.0.0.1:8001/health", "Real Backend Health"),
        ("http://127.0.0.1:8001/api/v1/prices/crypto/btc", "Real Backend BTC Price"),
        (
            "http://127.0.0.1:8001/api/v1/prices/bitcoin/history?period=1d",
            "Real Backend History",
        ),
        (
            "http://127.0.0.1:8001/api/v1/prices/bitcoin/full?days=1",
            "Real Backend Full Data",
        ),
        # Mock API (port 8002)
        ("http://127.0.0.1:8002/health", "Mock API Health"),
        ("http://127.0.0.1:8002/api/v1/prices/crypto/btc", "Mock API BTC Price"),
        (
            "http://127.0.0.1:8002/api/v1/prices/bitcoin/history?period=1d",
            "Mock API History",
        ),
        (
            "http://127.0.0.1:8002/api/v1/prices/bitcoin/full?days=1",
            "Mock API Full Data",
        ),
        ("http://127.0.0.1:8002/api/v1/cache/stats", "Mock API Cache Stats"),
    ]

    async with aiohttp.ClientSession() as session:
        results = []

        for url, name in test_cases:
            success = await test_endpoint(session, url, name)
            results.append((name, success))
            print()  # Empty line for readability

        print("\n📊 Test Results Summary:")
        print("=" * 50)
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {name}")

        # Summary
        passed = sum(1 for _, success in results if success)
        total = len(results)
        print(f"\n🎯 Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Both APIs are working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    print(f"⏰ Starting API tests at {datetime.now()}")
    asyncio.run(main())
