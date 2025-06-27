#!/usr/bin/env python3
"""
WealthOS Status Checker
Quick way to see which services are running and their health.
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def check_service(session, name, url, port):
    """Check if a service is running and healthy."""
    try:
        async with session.get(url, timeout=2) as response:
            if response.status == 200:
                if "health" in url:
                    data = await response.json()
                    return f"✅ {name} (Port {port}): Healthy"
                else:
                    return f"✅ {name} (Port {port}): Running"
            else:
                return (
                    f"⚠️  {name} (Port {port}): Responded but status {response.status}"
                )
    except Exception as e:
        return f"❌ {name} (Port {port}): Not running"


async def main():
    """Check all WealthOS services."""
    print("🚀 WealthOS Service Status Check")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    services = [
        ("Mock API", "http://localhost:8002/health", 8002),
        ("Real Backend", "http://localhost:8001/health", 8001),
        ("Frontend", "http://localhost:5173", 5173),
        (
            "Redis",
            "http://localhost:6379",
            6379,
        ),  # Note: This won't work for Redis directly
    ]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, url, port in services:
            if name != "Redis":  # Skip Redis HTTP check
                tasks.append(check_service(session, name, url, port))

        results = await asyncio.gather(*tasks)

        for result in results:
            print(result)

        # Special Redis check
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            print("✅ Redis (Port 6379): Running")
        except:
            print("❌ Redis (Port 6379): Not running")

    print()
    print("📊 Current Configuration:")
    try:
        # Read current API config
        with open("frontend/src/config/api.ts", "r") as f:
            content = f.read()
            if "CURRENT_MODE: ApiMode = 'MOCK'" in content:
                print("🎭 Mode: MOCK API (Fake data for testing)")
                print("🔗 URL: http://localhost:8002/api/v1")
            elif "CURRENT_MODE: ApiMode = 'REAL'" in content:
                print("🔗 Mode: REAL API (Live data from providers)")
                print("🔗 URL: http://localhost:8001/api/v1")
            else:
                print("⚠️  Mode: Unknown configuration")
    except Exception as e:
        print(f"⚠️  Could not read API config: {e}")

    print()
    print("💡 Quick Commands:")
    print("   Start Mock API:    python mock_api_server.py")
    print(
        "   Start Real Backend: cd backend && uv run uvicorn app.main:app --reload --port 8001"
    )
    print("   Start Frontend:    cd frontend && pnpm dev")
    print("   Test APIs:         python test_apis.py")
    print("   View Config:       cat CONFIG.md")


if __name__ == "__main__":
    asyncio.run(main())
