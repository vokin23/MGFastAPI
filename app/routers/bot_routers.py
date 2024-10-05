from datetime import timedelta

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.bot_schemas import UpdateVipStatus
from app.schemas.player_schemas import PlayerSchema
from app.service.base_service import get_moscow_time
from app.tasks.tasks import add_vip_task

bot_router = APIRouter(prefix="/bot")
admin_router = APIRouter(prefix="/bot")


@bot_router.post('/update_vip_status', summary='Обновление статуса VIP')
async def update_vip_status(data: UpdateVipStatus) -> PlayerSchema:
    async with async_session_maker() as session:
        steam_id = data.steam_id
        days = data.days
        vip_lvl = data.vip_lvl
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail='Игрок не найден')
        if player.vip and player.vip_lvl == vip_lvl:
            player.date_end_vip = player.date_end_vip + timedelta(days=days)
            await session.commit()
            return player
        elif player.vip and player.vip_lvl != vip_lvl:
            raise HTTPException(status_code=400, detail='У игрока уже есть VIP статус')
        player.vip = True
        player.created_at_vip = get_moscow_time()
        player.date_end_vip = get_moscow_time() + timedelta(days=days)
        player.vip_lvl = vip_lvl
        await session.commit()
        add_vip_task.delay(steam_id, vip_lvl)
        return player


@bot_router.post('/reseter_player', summary='Обнуление игрока')
async def reseter_player(data) -> PlayerSchema:
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.steam_id == data.steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail='Игрок не найден')
        await session.commit()
        return player
