import random
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.player_schemas import PlayerGetGameBalance

player_router = APIRouter(prefix="/player")


@player_router.get("/", summary="Получение списка игроков")
async def get_all_players() -> List[Player]:
    async with async_session_maker() as session:
        async with session() as s:
            result = await s.execute(select(Player))
            return result.scalars().all()


@player_router.get("/{steam_id}", summary="Получение информации об игроке")
async def get_player(steam_id: str = Query(..., description="SteamID игрока")) -> Player:
    async with async_session_maker() as session:
        async with session() as s:
            result = await s.execute(select(Player).where(Player.steam_id == steam_id))
            player = result.scalar()
            if player is None:
                raise HTTPException(status_code=404, detail="Игрок не найден")
            return player


@player_router.post("/{steam_id}", summary="Создание игрока")
async def create_player(steam_id: str = Query(..., description="SteamID игрока")) -> Player:
    async with async_session_maker() as session:
        async with session() as session:
            player = Player(steam_id=steam_id)
            session.add(player)
            await session.commit()
            return player


@player_router.get("/get_balance/{steam_id}", summary="Получение баланса по SteamID")
async def get_balance(steam_id: str = Query(description="SteamID игрока")) -> PlayerGetGameBalance:
    async with async_session_maker() as session:
        async with session() as session:
            result = await session.execute(select(Player).where(Player.steam_id == steam_id))
            player = result.scalar()
            if player is None:
                raise HTTPException(status_code=404, detail="Игрок не найден")
            return PlayerGetGameBalance(steam_id=player.steam_id, balance=player.game_balance)


@player_router.post("/money_withdrawal/{steam_id}", summary="Снятие денег по SteamID и money")
async def money_withdrawal(steam_id: str = Query(description="SteamID игрока"), money: int = Query(description="Сумма")) -> PlayerGetGameBalance:
    async with async_session_maker() as session:
        async with session() as session:
            result = await session.execute(select(Player).where(Player.steam_id == steam_id))
            player = result.scalar()
            if player is None:
                raise HTTPException(status_code=404, detail="Игрок не найден")
            if player.game_balance - money < 0:
                raise HTTPException(status_code=400, detail="Недостаточно средств")
            player.game_balance -= money
            await session.commit()
            return PlayerGetGameBalance(steam_id=player.steam_id, balance=player.game_balance)


@player_router.post("/replenishment_of_balance/{steam_id}", summary="Пополнение баланса по SteamID и money")
async def replenishment_of_balance(steam_id: str = Query(description="SteamID игрока"), money: int = Query(description="Сумма")) -> PlayerGetGameBalance:
    async with async_session_maker() as session:
        async with session() as session:
            result = await session.execute(select(Player).where(Player.steam_id == steam_id))
            player = result.scalar()
            if player is None:
                raise HTTPException(status_code=404, detail="Игрок не найден")
            player.game_balance += money
            await session.commit()
            return PlayerGetGameBalance(steam_id=player.steam_id, balance=player.game_balance)
