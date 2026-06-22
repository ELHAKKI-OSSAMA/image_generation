from typing import Dict, Any, Optional, List
from uuid import UUID
import json
from redis import Redis
from fastapi import Depends

from core.config import get_settings
from core.dependencies import get_redis

class PermissionCache:
    """Cache service for user permissions."""
    
    def __init__(self, redis: Redis = Depends(get_redis)):
        """Initialize permission cache with Redis backend."""
        self.settings = get_settings()
        self.redis = redis
        self.ttl = self.settings.PERMISSION_CACHE_TTL  # Default 1 hour

    async def get(self, key: str) -> Optional[List[str]]:
        """Get cached permissions by key."""
        if cached := await self.redis.get(key):
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                return None
        return None

    async def set(self, key: str, permissions: List[str]) -> None:
        """Cache permissions with key."""
        await self.redis.set(
            key,
            json.dumps(permissions),
            ex=self.ttl
        )

    async def delete(self, key: str) -> None:
        """Delete cached permissions by key."""
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def clear_user_permissions(self, user_id: UUID) -> None:
        """Clear all permission caches for a user."""
        await self.delete_pattern(f"perm:{user_id}:*")

    async def clear_org_permissions(self, org_id: UUID) -> None:
        """Clear all permission caches for an organization."""
        await self.delete_pattern(f"perm:*:{org_id}")

    async def clear_role_permissions(self, role: str) -> None:
        """Clear permission caches for all users with a specific role."""
        await self.delete_pattern(f"perm:role:{role}:*")
