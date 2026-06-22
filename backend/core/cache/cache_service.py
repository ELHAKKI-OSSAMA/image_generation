from typing import Optional, Any
from uuid import UUID
import json
from cachetools import TTLCache
from redis import Redis
from fastapi import Depends

from core.config import get_settings
from core.dependencies import get_redis

class CacheService:
    """Multi-level caching service implementation."""
    
    def __init__(self, redis: Redis = Depends(get_redis)):
        """Initialize cache service with L1 (memory) and L2 (Redis) caches."""
        self.settings = get_settings()
        # L1 Cache (In-Memory with 1 minute TTL)
        self.local_cache = TTLCache(
            maxsize=self.settings.CACHE_LOCAL_MAXSIZE,
            ttl=self.settings.CACHE_LOCAL_TTL
        )
        # L2 Cache (Redis)
        self.redis = redis

    async def get(self, key: str, namespace: str = "") -> Optional[Any]:
        """Get value from cache, trying L1 then L2."""
        cache_key = f"{namespace}:{key}" if namespace else key

        # Try L1 cache first
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]

        # Try L2 cache
        if cached := await self.redis.get(cache_key):
            # Update L1 cache
            try:
                value = json.loads(cached)
                self.local_cache[cache_key] = value
                return value
            except json.JSONDecodeError:
                return cached

        return None

    async def set(
        self,
        key: str,
        value: Any,
        namespace: str = "",
        expire: int = None
    ) -> None:
        """Set value in both L1 and L2 caches."""
        cache_key = f"{namespace}:{key}" if namespace else key
        
        # Set in L1 cache
        self.local_cache[cache_key] = value
        
        # Set in L2 cache
        try:
            cached_value = json.dumps(value)
        except (TypeError, ValueError):
            cached_value = str(value)
            
        if expire:
            await self.redis.set(cache_key, cached_value, ex=expire)
        else:
            await self.redis.set(cache_key, cached_value)

    async def delete(self, key: str, namespace: str = "") -> None:
        """Remove value from both caches."""
        cache_key = f"{namespace}:{key}" if namespace else key
        
        # Remove from L1
        self.local_cache.pop(cache_key, None)
        
        # Remove from L2
        await self.redis.delete(cache_key)

    async def get_organization(self, org_id: UUID) -> Optional[dict]:
        """Get organization data from cache."""
        return await self.get(str(org_id), namespace="org")

    async def set_organization(
        self,
        org_id: UUID,
        data: dict,
        expire: int = None
    ) -> None:
        """Cache organization data."""
        await self.set(str(org_id), data, namespace="org", expire=expire)

    async def invalidate_organization(self, org_id: UUID) -> None:
        """Invalidate organization cache."""
        await self.delete(str(org_id), namespace="org")

    async def clear_all(self) -> None:
        """Clear all caches (useful for testing)."""
        self.local_cache.clear()
        await self.redis.flushdb()
