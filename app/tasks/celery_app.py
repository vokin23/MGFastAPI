from celery import Celery

from app import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "app.tasks.tasks"
    ]
)

celery_app.conf.beat_schedule = {
    "vips": {
        "task": "cheek_vips",
        "schedule": 3600
    }
}
