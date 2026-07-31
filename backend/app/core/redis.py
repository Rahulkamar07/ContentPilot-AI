
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

redis_client: aioredis.Redis | None = None


async def init_redis_client() -> aioredis.Redis:
    """Initializes async Redis connection pool."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0,
        )
        logger.info("Async Redis client initialized successfully")
    return redis_client


async def close_redis_client() -> None:
    """Gracefully closes Redis connection pool."""
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        logger.info("Async Redis client connection closed")
        redis_client = None


async def get_redis() -> aioredis.Redis:
    """Dependency provider for async Redis client."""
    if redis_client is None:
        return await init_redis_client()
    return redis_client
