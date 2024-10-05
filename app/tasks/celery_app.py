from celery import Celery
from celery.schedules import crontab

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
        "schedule": crontab(hour=0, minute=0)
    },
    "player_info": {
        "task": "update_player_info",
        "schedule": 20
    }
}