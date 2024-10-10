import json
import os

import aiofiles
import pytz
from datetime import datetime

from sqlalchemy import select, func, insert

from app.models import Player
from app.models.datebase import async_session_maker_null_pool
from app.models.player_model import Fraction


def get_moscow_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz).replace(tzinfo=None)
    return moscow_time


async def read_json_async(file_path):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        contents = await f.read()
        return json.loads(contents)


async def write_json_async(file_path, data):
    async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))


async def get_vips_player():
    async with async_session_maker_null_pool() as session:
        players_obj = select(Player).filter(Player.vip, func.date(Player.date_end_vip) == get_moscow_time().date())
        players_smtm = await session.execute(players_obj)
        players = players_smtm.scalars().all()
        if players:
            for player in players:
                player.vip_lvl = 0
                player.vip = False
                player.created_at_vip = None
                player.date_end_vip = None
            await session.commit()


async def update_player_info():
    directory_path = '/app/PlayersDB'
    files = os.listdir(directory_path)
    for file in files:
        async with async_session_maker_null_pool() as session:
            player = await read_json_async(f'{directory_path}/{file}')
            steam_id = str(file).split(".")[0]
            player_obj = await session.execute(select(Player).where(Player.steam_id == steam_id))
            player_db = player_obj.scalar()
            if player_db is None:
                continue
            player_db.name = player['Name']
            player_db.surname = player['Surname']
            player_db.avatar = player['Avatar']
            player_db.about = player['About']
            player_db.exp = player['EXP']
            player_db.fraction_id = player['FractionID']
            player_db.survivor_model = player['SurvivorModel']
            await session.commit()


async def update_fraction_info():
    directory_path_profiles = '/app/MGStalker'
    directory_path_fraction = '/app/MGStalker/Fractions'
    base_fractions = await read_json_async(f'{directory_path_profiles}/Fractions.json')
    async with async_session_maker_null_pool() as session:
        for fraction in base_fractions['Fractions']:
            fraction_id = fraction['FractionID']
            fraction_name = fraction['Name']
            fraction_logo = fraction['Logo']
            fraction_json = fraction['FractionJson']
            fraction_main = await read_json_async(f'{directory_path_fraction}/{fraction_json}')
            leader_steam_id = fraction_main['LeaderSteamID']
            leader_name = fraction_main['LeaderName']
            spawn_pos = fraction_main['SpawnPos']
            max_staff = fraction_main['MaxStaff']

            fraction_obj = await session.execute(select(Fraction).where(Fraction.fraction_id == fraction_id))
            fraction_db = fraction_obj.scalar()
            if fraction_db:
                fraction_db.name = fraction_name
                fraction_db.leader_steam_id = leader_steam_id
                fraction_db.leader_name = leader_name
                fraction_db.logo = fraction_logo
                fraction_db.spawn_pos = spawn_pos
                fraction_db.max_staff = max_staff
            else:
                new_fraction = insert(Fraction).values(
                    fraction_id=fraction_id,
                    name=fraction_name,
                    leader_steam_id=leader_steam_id,
                    leader_name=leader_name,
                    logo=fraction_logo,
                    spawn_pos=spawn_pos,
                    max_staff=max_staff
                )
                await session.execute(new_fraction)
                await session.commit()


async def add_vip_status(steam_id, vip_lvl):
    file_path = '/app/PlayersDB'
    data_player = await read_json_async(f"{file_path}/{steam_id}.json")
    data_player['VIP_Lvl'] = vip_lvl
    await write_json_async(f"{file_path}/{steam_id}.json", data_player)
