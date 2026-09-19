from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from celery.utils.log import get_task_logger

from app.core.database import AsyncSessionFactory
from app.services.publishing import publish_due_posts
from app.services.rss_ingestion import ingest_source
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.workers.tasks.system_health_ping")
def system_health_ping() -> dict[str, Any]:
    """Periodic background health ping task confirming worker responsiveness."""
    timestamp = datetime.now(UTC).isoformat()
    logger.info("Celery worker health ping executed successfully at %s", timestamp)
    return {
        "status": "PONG",
        "timestamp": timestamp,
        "worker": "celery_worker",
    }


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="app.workers.tasks.ingest_rss_source_task",
)
def ingest_rss_source_task(self, workspace_id: str, source_id: str) -> dict[str, int]:  # noqa: ANN001
    async def _run() -> dict[str, int]:
        async with AsyncSessionFactory() as session:
            return await ingest_source(
                session,
                workspace_id=UUID(workspace_id),
                source_id=UUID(source_id),
            )

    result = asyncio.run(_run())
    logger.info(
        "RSS ingestion completed",
        workspace_id=workspace_id,
        source_id=source_id,
        **result,
    )
    return result


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="app.workers.tasks.publish_scheduled_posts_task",
)
def publish_scheduled_posts_task(self) -> dict[str, int]:  # noqa: ANN001
    async def _run() -> int:
        async with AsyncSessionFactory() as session:
            return await publish_due_posts(session)

    published_count = asyncio.run(_run())
    logger.info("Scheduled publishing run complete", published_count=published_count)
    return {"published_count": published_count}
