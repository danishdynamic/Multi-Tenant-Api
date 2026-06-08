import json
import redis.asyncio as redis
from typing import Any, Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url)
        self._connected = False

    async def _ensure_connection(self):
        """Ensure Redis connection is established"""
        if not self._connected:
            try:
                await self.redis.ping()
                self._connected = True
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            await self._ensure_connection()
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = settings.cache_ttl) -> bool:
        """Set value in cache with TTL"""
        try:
            await self._ensure_connection()
            await self.redis.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self._ensure_connection()
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            await self._ensure_connection()
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def get_or_set(self, key: str, fetch_func, ttl: int = settings.cache_ttl):
        """Get from cache or set if not exists"""
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value

        # Fetch fresh data
        fresh_value = await fetch_func()
        if fresh_value is not None:
            await self.set(key, fresh_value, ttl)

        return fresh_value

    async def invalidate_tenant_cache(self, tenant_id: int):
        """Invalidate all cache entries for a tenant"""
        patterns = [
            f"tenant_{tenant_id}_*",
            f"user_*_tenant_{tenant_id}_*",
            f"dashboard_*_tenant_{tenant_id}",
            f"analytics_tenant_{tenant_id}_*"
        ]

        total_deleted = 0
        for pattern in patterns:
            total_deleted += await self.delete_pattern(pattern)

        logger.info(f"Invalidated {total_deleted} cache entries for tenant {tenant_id}")
        return total_deleted

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("Redis connection closed")

cache = Cache()