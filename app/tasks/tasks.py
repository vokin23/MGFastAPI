import asyncio

from app.service.base_service import get_vips_player
from app.tasks.celery_app import celery_instance


@celery_instance.task(name="cheek_vips")
def cheek_vips_everyday():
    asyncio.run(get_vips_player())
