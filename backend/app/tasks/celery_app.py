from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "aifactory",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.generation_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "generate-daily-content": {
            "task": "app.tasks.generation_tasks.generate_daily_content",
            "schedule": 3600.0 * 6,  # Every 6 hours
        },
    },
)
