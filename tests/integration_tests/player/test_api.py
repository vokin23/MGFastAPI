import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.main import app
from app.models import Player
from app.models.datebase import async_session_maker_null_pool
from tests.conftest import base_url


async def get_players():
    async with async_session_maker_null_pool() as session:
        result = await session.execute(select(Player))
        return result.scalars().all()


async def get_player(steam_id):
    async with async_session_maker_null_pool() as session:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        return result.scalar()


async def test_create_player(patch_player_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        await ac.post("/v1/player/", params={"steam_id": "testplayer"})
        player = await get_player("testplayer")
        assert player


async def test_get_players(patch_player_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/v1/admin/player/get_all_players")
        assert response.status_code == 200


async def test_get_balance(patch_player_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        players = await get_players()
        for player in players:
            response = await ac.get(f"/v1/player/get_balance/", params={"steam_id": player.steam_id})
            assert response.status_code == 200


async def test_money_withdrawal(patch_player_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        players = await get_players()
        for player in players:
            response = await ac.post(f"/v1/player/money_withdrawal/", params={"steam_id": player.steam_id, "money": 100})
            assert response.status_code == 200


async def test_replenishment_of_balance(patch_player_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        players = await get_players()
        for player in players:
            response = await ac.post(f"/v1/player/replenishment_of_balance/", params={"steam_id": player.steam_id, "money": 300})
            assert response.status_code == 200
