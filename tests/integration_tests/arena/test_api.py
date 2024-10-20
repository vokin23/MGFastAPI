import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.init import redis_manager
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


@pytest.mark.asyncio
async def test_create_arenas(patch_arena_async_session_maker):
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


@pytest.mark.asyncio
async def test_get_arenas(patch_arena_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/v1/admin/arena/get_arenas")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_arena(patch_arena_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/v1/admin/arena/get_arena?arena_id=1")
        assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_update_arena(patch_arena_async_session_maker):
#     async with AsyncClient(app=app, base_url=base_url) as ac:
#         response = await ac.put("/v1/admin/arena/update_arena?arena_id=1", params={"arena_id": 1}, json={
#             "name": "test",
#             "description": "test",
#             "cords_spawn": [],
#             "cloths": [],
#             "free": True
#         })
#         assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_patch_arena(patch_arena_async_session_maker):
#     async with AsyncClient(app=app, base_url=base_url) as ac:
#         response = await ac.patch("/v1/admin/arena/patch_arena?arena_id=2", params={"arena_id": 2}, json={
#             "name": "test_patch",
#             "description": "test_patch",
#             "cords_spawn": [],
#             "cloths": [],
#             "free": True
#         })
#         assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_arena(patch_arena_async_session_maker):
    players = await get_players()
    await redis_manager.connect()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        for player in players:
            response = await ac.post("/v1/arena/register_arena", json={
                "steam_id": player.steam_id,
                "items": [{}, {}, {}],
                "position": [player.steam_id, player.steam_id, player.steam_id],
                "orientation": [player.steam_id, player.steam_id, player.steam_id]
            })
            assert response.status_code == 200
    await redis_manager.close()


async def test_post_action_arena(patch_action_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        jsons = await read_json_async("tests/data/action.json")
        for json in jsons:
            response = await ac.post("/v1/action/action", json=json)
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_register_arena(patch_arena_async_session_maker):
    players = await get_players()
    await redis_manager.connect()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        for player in players:
            response = await ac.post("/v1/arena/register_arena", json={
                "steam_id": player.steam_id,
                "items": [{}, {}, {}],
                "position": [player.steam_id, player.steam_id, player.steam_id],
                "orientation": [player.steam_id, player.steam_id, player.steam_id]
            })
            assert response.status_code == 200

            response = await ac.post("/v1/arena/delete_register_arena", json={
                "steam_id": player.steam_id
            })
            assert response.status_code == 200
    await redis_manager.close()


async def test_stats_arena_pda(patch_arena_async_session_maker):
    players = await get_players()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        for player in players:
            response = await ac.get("/v1/arena/stats_arena_pda", params={"steam_id": player.steam_id})
            assert response.status_code == 200