import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.quest_model import ReputationType, Operator
from app.service.base_service import read_json_async
from app.main import app
from app.models import Player
from app.models.datebase import async_session_maker_null_pool
from tests.conftest import base_url


async def get_players():
    async with async_session_maker_null_pool() as session:
        result = await session.execute(select(Player))
        return result.scalars().all()


async def test_create_arenas(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        arenas = await read_json_async("tests/data/arenas.json")
        for arena in arenas:
            response = await ac.post("/v1/admin/arena/create_arena", json={
                "name": arena["name"],
                "description": arena["description"],
                "cords_spawn": arena["cords_spawn"],
                "cloths": arena["cloths"],
                "free": arena["free"]
            })
            assert response.status_code == 200


async def test_get_arenas(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/v1/admin/arena/get_arenas")
        assert response.status_code == 200


async def test_get_arena(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/v1/admin/arena/get_arena?arena_id=1")
        assert response.status_code == 200


async def test_update_arena(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.put("/v1/admin/arena/update_arena?arena_id=1", json={
            "name": "test",
            "description": "test",
            "cords_spawn": [],
            "cloths": [],
            "free": True
        })
        assert response.status_code == 200


async def test_patch_arena(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.patch("/v1/admin/arena/patch_arena?arena_id=1", json={
            "name": "test_patch",
            "description": "test_patch",
            "cords_spawn": ["test_patch"],
            "cloths": ["test_patch"],
            "free": True
        })
        assert response.status_code == 200


async def test_register_arena(patch_quest_async_session_maker):
    players = await get_players()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        for player in players:
            response = await ac.post("/v1/arena/register_arena", json={
                "steam_id": player.steam_id,
                "items": [player.steam_id, player.steam_id, player.steam_id],
                "position": player.steam_id,
                "orientation": player.steam_id
            })
            assert response.status_code == 200


async def test_delete_register_arena(patch_quest_async_session_maker):
    players = await get_players()
    player = players[0]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post("/v1/arena/delete_register_arena", json={
            "steam_id": player.steam_id
        })
        assert response.status_code == 200