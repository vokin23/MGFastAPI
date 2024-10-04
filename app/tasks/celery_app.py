from celery import Celery

from app import settings

celery_instance = Celery(
    "tasks",
    broker=settings.redis_url,
    include=[
        "app.tasks.tasks"
    ]
)

celery_instance.conf.beat_schedule = {
    "vips": {
        "task": "cheek_vips",
        "schedule": 5
    }
}
