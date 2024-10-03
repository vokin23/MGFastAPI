import json

import aiofiles
import pytz
from datetime import datetime

from sqlalchemy import select

from app.models import Player
from app.models.datebase import async_session_maker_null_pool


def get_moscow_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz).replace(tzinfo=None)
    return moscow_time


async def read_json_async(file_path):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        contents = await f.read()
        return json.loads(contents)


async def get_vips_player():
    async with async_session_maker_null_pool() as session:
        players_obj = select(Player).filter(Player.vip, Player.date_end_vip.date() == get_moscow_time().date())
        players_smtm = await session.execute(players_obj)
        players = players_smtm.scalars().all()
        if players:
            for player in players:
                player.vip_lvl = 0
                player.vip = False
                player.created_at_vip = None
                player.date_end_vip = None
            await session.commit()
