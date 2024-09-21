import random
from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.quest_model import ReputationType
from app.schemas.player_schemas import PlayerGetGameBalanceSchema, PlayerSchema, PlayerUpdateSchema

player_router = APIRouter(prefix="/player")
admin_router = APIRouter()


@admin_router.get("/get_all_players", summary="Получение списка игроков")
async def get_all_players() -> List[PlayerSchema]:
    async with async_session_maker() as session:
        result = await session.execute(select(Player))
        return result.scalars().all()


@admin_router.get("/info_player", summary="Получение информации об игроке")
async def get_player(steam_id: str = Query(..., description="SteamID игрока")) -> PlayerSchema:
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        return player


@player_router.post("/", summary="Создание игрока")
async def create_player(steam_id: str = Query(..., description="SteamID игрока")) -> PlayerSchema:
    async with async_session_maker() as session:
        datetime_now = datetime.now()
        reputations_obj = select(ReputationType)
        reputations = await session.execute(reputations_obj)
        list_reputations = reputations.scalars().all()
        reputation = []
        for rep in list_reputations:
            reputation.append({
                "name": rep.name,
                "level": 0
            })
        player_obj = insert(Player).values(steam_id=steam_id,
                                           game_balance=10000,
                                           reputation=reputation,
                                           created_at_player=datetime_now,
                                           created_at_vip=None,
                                           date_end_vip=None).returning(Player)
        player = await session.execute(player_obj)
        await session.commit()
        return player.scalar()


@player_router.get("/get_balance/", summary="Получение баланса по SteamID")
async def get_balance(steam_id: str = Query(description="SteamID игрока")) -> PlayerGetGameBalanceSchema:
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        return PlayerGetGameBalanceSchema(steam_id=player.steam_id, balance=player.game_balance)


@player_router.post("/money_withdrawal/", summary="Снятие денег по SteamID и money")
async def money_withdrawal(steam_id: str = Query(description="SteamID игрока"),
                           money: int = Query(description="Сумма")) -> PlayerGetGameBalanceSchema:
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        if player.game_balance - money < 0:
            raise HTTPException(status_code=400, detail="Недостаточно средств")
        player.game_balance -= money
        await session.commit()
        return PlayerGetGameBalanceSchema(steam_id=player.steam_id, balance=player.game_balance)


@player_router.post("/replenishment_of_balance/", summary="Пополнение баланса по SteamID и money")
async def replenishment_of_balance(steam_id: str = Query(description="SteamID игрока"),
                                   money: int = Query(description="Сумма")) -> PlayerGetGameBalanceSchema:
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        player.game_balance += money
        await session.commit()
        return PlayerGetGameBalanceSchema(steam_id=player.steam_id, balance=player.game_balance)


@admin_router.put("/put_player", summary="Обновление информации игрока")
async def put_player(data_player: PlayerUpdateSchema,
                     steam_id: str = Query(..., description="SteamID игрока")) -> PlayerSchema:
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = result.scalar()
        if player is None:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        if data_player.reputation is None:
            data_player.reputation = player.reputation
        if data_player.created_at_vip is None:
            data_player.created_at_vip = player.created_at_vip
        if data_player.date_end_vip is None:
            data_player.date_end_vip = player.date_end_vip
        player.game_balance = data_player.game_balance
        player.site_balance = data_player.site_balance
        player.vip = data_player.vip
        player.vip_lvl = data_player.vip_lvl
        data_player.reputation = [rep.dict() for rep in data_player.reputation]
        player.reputation = data_player.reputation
        player.created_at_vip = data_player.created_at_vip
        player.date_end_vip = data_player.date_end_vip
        await session.commit()
        return player
