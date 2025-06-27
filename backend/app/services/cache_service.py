"""
Enhanced caching service with Redis backend and proper data storage patterns.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from fastapi import HTTPException
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Enhanced caching service with Redis backend and data persistence."""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to Redis server."""
        try:
            self.redis = redis.from_url(
                "redis://localhost:6379",
                encoding="utf8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            await self.redis.ping()
            self.connected = True
            logger.info("✅ Redis cache service connected successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("Redis cache service disconnected")

    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate standardized cache key."""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)

    async def get_bitcoin_price(
        self, currency: str = "usd"
    ) -> Optional[Dict[str, Any]]:
        """Get cached Bitcoin current price."""
        if not self.connected:
            return None

        try:
            key = self._get_cache_key("btc:price", currency=currency)
            cached = await self.redis.get(key)

            if cached:
                data = json.loads(cached)
                logger.info(f"📦 Cache HIT: Bitcoin price ({currency})")
                return data

            logger.info(f"📭 Cache MISS: Bitcoin price ({currency})")
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set_bitcoin_price(
        self, price: float, currency: str = "usd", ttl_seconds: int = 30
    ) -> bool:
        """Cache Bitcoin current price with TTL."""
        if not self.connected:
            return False

        try:
            key = self._get_cache_key("btc:price", currency=currency)
            data = {
                "price": price,
                "currency": currency,
                "timestamp": datetime.now().isoformat(),
                "cached_at": datetime.now().timestamp(),
            }

            await self.redis.setex(key, ttl_seconds, json.dumps(data))
            logger.info(
                f"💾 Cached Bitcoin price: ${price:,.2f} {currency.upper()} (TTL: {ttl_seconds}s)"
            )
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def get_bitcoin_history(
        self, period: str, currency: str = "usd"
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached Bitcoin historical data."""
        if not self.connected:
            return None

        try:
            key = self._get_cache_key("btc:history", period=period, currency=currency)
            cached = await self.redis.get(key)

            if cached:
                data = json.loads(cached)
                logger.info(
                    f"📦 Cache HIT: Bitcoin history ({period}, {currency}) - {len(data.get('data', []))} points"
                )
                return data

            logger.info(f"📭 Cache MISS: Bitcoin history ({period}, {currency})")
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set_bitcoin_history(
        self,
        historical_data: List[Dict[str, Any]],
        period: str,
        currency: str = "usd",
        ttl_seconds: int = 300,  # 5 minutes for historical data
    ) -> bool:
        """Cache Bitcoin historical data with TTL."""
        if not self.connected:
            return False

        try:
            key = self._get_cache_key("btc:history", period=period, currency=currency)

            # Store with metadata
            cache_data = {
                "data": historical_data,
                "period": period,
                "currency": currency,
                "count": len(historical_data),
                "cached_at": datetime.now().isoformat(),
                "expires_at": (
                    datetime.now() + timedelta(seconds=ttl_seconds)
                ).isoformat(),
            }

            await self.redis.setex(key, ttl_seconds, json.dumps(cache_data))
            logger.info(
                f"💾 Cached Bitcoin history: {len(historical_data)} points for {period} (TTL: {ttl_seconds}s)"
            )
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def store_api_response(
        self, endpoint: str, response_data: Any, ttl_seconds: int = 60
    ) -> bool:
        """Store raw API response for debugging and analytics."""
        if not self.connected:
            return False

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f"api_response:{endpoint}:{timestamp}"

            metadata = {
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
                "data": response_data,
                "size_bytes": len(str(response_data)),
            }

            await self.redis.setex(key, ttl_seconds, json.dumps(metadata))
            logger.debug(
                f"📥 Stored API response: {endpoint} ({metadata['size_bytes']} bytes)"
            )
            return True

        except Exception as e:
            logger.error(f"API response storage error: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health info."""
        if not self.connected:
            return {"status": "disconnected", "redis_available": False}

        try:
            info = await self.redis.info()

            # Count our Bitcoin-related keys
            btc_keys = await self.redis.keys("btc:*")
            api_keys = await self.redis.keys("api_response:*")

            return {
                "status": "connected",
                "redis_available": True,
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "bitcoin_cache_keys": len(btc_keys),
                "api_response_keys": len(api_keys),
                "total_keys": len(btc_keys) + len(api_keys),
            }

        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "error": str(e)}

    async def clear_bitcoin_cache(self) -> bool:
        """Clear all Bitcoin-related cache entries."""
        if not self.connected:
            return False

        try:
            btc_keys = await self.redis.keys("btc:*")
            if btc_keys:
                await self.redis.delete(*btc_keys)
                logger.info(f"🗑️ Cleared {len(btc_keys)} Bitcoin cache entries")
            return True

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """FastAPI dependency to get cache service."""
    return cache_service
