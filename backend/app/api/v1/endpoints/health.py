from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.redis import get_redis

router = APIRouter()


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Returns 200 OK if the FastAPI web application process is running."
)
async def liveness_probe() -> dict[str, Any]:
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Probes PostgreSQL database and Redis connections to verify service readiness."
)
async def readiness_probe(
    db: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis)
) -> dict[str, Any]:
    db_healthy = False
    redis_healthy = False

    # Check Database connection
    try:
        await db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    # Check Redis connection
    try:
        await redis.ping()
        redis_healthy = True
    except Exception:
        redis_healthy = False

    is_ready = db_healthy and redis_healthy
    response_status = "READY" if is_ready else "NOT_READY"

    return {
        "status": response_status,
        "components": {
            "database": "UP" if db_healthy else "DOWN",
            "redis": "UP" if redis_healthy else "DOWN"
        }
    }


@router.get(
    "/version",
    status_code=status.HTTP_200_OK,
    summary="Application Version Information",
    description="Returns application release version, git commit hash, and environment details."
)
async def version_info() -> dict[str, Any]:
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "git_commit": settings.GIT_COMMIT,
        "api_v1_prefix": settings.API_V1_STR
    }
