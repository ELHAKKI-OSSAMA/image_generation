# core/redis.py
import aioredis
from typing import Optional, Awaitable

async def get_redis(url: str = "redis://localhost", decode: bool = True) -> Awaitable[aioredis.Redis]:
    """Get a Redis client with proper configuration."""
    return await aioredis.create_redis_pool(
        url,
        encoding="utf-8" if decode else None,
        timeout=5,
    )

# Default Redis instance
redis = None

async def init_redis():
    """Initialize Redis connection and return the client."""
    global redis
    try:
        redis = await get_redis()
        await redis.ping()  # Test the connection
        return redis
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        redis = None
        return None