from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "contentpilot_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,        # 5 mins hard limit
    task_soft_time_limit=240,   # 4 mins soft limit
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
)

# Celery Beat Periodic Schedule
celery_app.conf.beat_schedule = {
    "celery-health-ping-every-15-min": {
        "task": "app.workers.tasks.system_health_ping",
        "schedule": crontab(minute="*/15"),
    },
}
