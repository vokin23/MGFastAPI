import random
from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.quest_model import ReputationType
from app.schemas.player_schemas import PlayerGetGameBalanceSchema, PlayerSchema

player_router = APIRouter(prefix="/player")


@player_router.get("/", summary="Получение списка игроков")
async def get_all_players() -> List[PlayerSchema]:
    async with async_session_maker() as session:
        result = await session.execute(select(Player))
        return result.scalars().all()


@player_router.get("/", summary="Получение информации об игроке")
async def get_player(steam_id: str = Query(..., description="SteamID игрока")) -> PlayerSchema:
    async with async_session_maker() as session:
        async with session() as s:
            result = await s.execute(select(Player).where(Player.steam_id == steam_id))
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
                                           created_at_player=datetime_now).returning(Player)
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
