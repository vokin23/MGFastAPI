import asyncio

from app.service.base_service import get_vips_player, update_player_info, add_vip_status, update_fraction_info
from app.tasks.celery_app import celery_instance


@celery_instance.task(name="cheek_vips")
def cheek_vips_everyday():
    asyncio.run(get_vips_player())
    print("cheek_vips_everyday успешно завершена!")


@celery_instance.task(name="update_player_info")
def update_player_info_task():
    asyncio.run(update_player_info())
    print("update_player_info_task успешно завершена!")


@celery_instance.task(name="update_fraction_info")
def update_fraction_info_task():
    asyncio.run(update_fraction_info())
    print("update_fraction_info_task успешно завершена!")


@celery_instance.task(name="add_vip")
def add_vip_task(steam_id, vip_lvl):
    asyncio.run(add_vip_status(steam_id, vip_lvl))
    print("add_vip_task успешно завершена!")

