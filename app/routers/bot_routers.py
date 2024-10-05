from datetime import timedelta

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.bot_schemas import UpdateVipStatus
from app.service.base_service import get_moscow_time

bot_router = APIRouter(prefix="/bot")
admin_router = APIRouter(prefix="/bot")


@bot_router.post('/update_vip_status', summary='Обновление статуса VIP')
async def update_vip_status(data: UpdateVipStatus) -> Player:
    async with async_session_maker() as session:
        steam_id = data.steam_id
        days = data.days
        vip_lvl = data.vip_lvl
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail='Игрок не найден')
        player.created_at_vip = get_moscow_time()
        player.date_end_vip = get_moscow_time() + timedelta(days=days)
        player.vip_lvl = vip_lvl
        await session.commit()
        return player
