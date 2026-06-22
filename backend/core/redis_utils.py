# core/redis_utils.py
from datetime import timedelta
from typing import Dict, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)

# redis_utils.py

import aioredis
from typing import Awaitable





async def get_redis(
    url: str = "redis://localhost",
    decode: bool = True
) -> Awaitable[aioredis.Redis]:
    """Create and return a Redis connection pool."""
    return await aioredis.create_redis_pool(
        url,
        encoding="utf-8" if decode else None,
        timeout=5,
    )


async def set_event_context(redis_client, user_id, event_id, ttl_seconds):
    key = f"user_ctx:{user_id}"
    await redis_client.hset(key, "event_id", str(event_id))
    await redis_client.expire(key, ttl_seconds)

async def get_event_context(redis_client, user_id, decode=True):
    key = f"user_ctx:{user_id}"
    try:
        ctx = await redis_client.hgetall(key)
        if not ctx:
            return None, None
        
        event_id = ctx.get("event_id" if decode else b"event_id")
        
        if not event_id:
            return None, None
        
        if not decode and isinstance(event_id, bytes):
            event_id = event_id.decode()
        
        return event_id
    except Exception as e:
        logger.error(f"Error in get_event_context: {e}")
        if os.getenv("ENV") == "production":
            raise
        return None

async def set_guest_context(redis_client, user_id, event_id, guest_id, ttl_seconds):
    """Set guest context in Redis with proper UUID handling"""
    key = f"user_ctx:{user_id}"
    await redis_client.hset(key, "event_id", str(event_id))
    await redis_client.hset(key, "guest_id", str(guest_id))  # Convert UUID to string
    await redis_client.expire(key, ttl_seconds)

async def get_guest_context(redis_client, user_id, decode=True):
    """Get guest context from Redis with proper UUID handling"""
    key = f"user_ctx:{user_id}"
    try:
        ctx = await redis_client.hgetall(key)
        if not ctx:
            return None, None
        
        event_id = ctx.get("event_id" if decode else b"event_id")
        guest_id = ctx.get("guest_id" if decode else b"guest_id")
        
        if not decode:
            # Convert bytes to string if needed
            if isinstance(event_id, bytes):
                event_id = event_id.decode()
            if isinstance(guest_id, bytes):
                guest_id = guest_id.decode()
        
        return event_id, guest_id
    except Exception as e:
        logger.error(f"Error in get_guest_context: {e}")
        if os.getenv("ENV") == "production":
            raise
        return None, None