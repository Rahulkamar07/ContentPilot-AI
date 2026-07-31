from typing import Dict, Any
from datetime import datetime, timezone
from celery.utils.log import get_task_logger
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.workers.tasks.system_health_ping")
def system_health_ping() -> Dict[str, Any]:
    """Periodic background health ping task confirming worker responsiveness."""
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"Celery worker health ping executed successfully at {timestamp}")
    return {
        "status": "PONG",
        "timestamp": timestamp,
        "worker": "celery_worker"
    }
