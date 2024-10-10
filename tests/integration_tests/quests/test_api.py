import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.quest_model import ReputationType, Operator
from app.service.base_service import read_json_async
from app.main import app
from app.models import Player
from app.models.datebase import async_session_maker_null_pool
from tests.conftest import base_url


async def get_reputation_type():
    async with async_session_maker_null_pool() as session:
        result = await session.execute(select(ReputationType))
        return result.scalars().all()


async def get_operators():
    async with async_session_maker_null_pool() as session:
        result = await session.execute(select(Operator))
        return result.scalars().all()


@pytest.mark.asyncio
async def test_create_operators(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        reputations_types = await get_reputation_type()
        for reputation_type in reputations_types:
            response = await ac.post("/v1/admin/quest/create_operator", json={
                "name": reputation_type.name,
                "description": "string",
                "class_name": "string",
                "reputation_type_id": reputation_type.id,
                "position": "1111 2222 3333",
                "orientation": "444 5555 6666",
                "clothes": [
                    "string",
                    "string",
                    "string"
                ]
            })
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_quest(patch_quest_async_session_maker):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        operators = await get_operators()
        for operator in operators:
            for type in ["daily", "weekly", "monthly", "lore"]:
                response = await ac.post("/v1/admin/quest/create_quest", json=
                {
                    "name": "string",
                    "type": type,
                    "title": "string",
                    "description": "string",
                    "awards_api": None,
                    "required_items": None,
                    "awards": [
                        {
                            "classname": "string",
                            "count": 0
                        }
                    ],
                    "conditions": [
                        {
                            "condition_name": "string",
                            "progress": "string",
                            "need": "string"
                        }
                    ],
                    "operator_id": operator.id,
                    "reputation_need": 0,
                    "reputation_add": 0,
                    "reputation_minus": 0
                })
                assert response.status_code == 200
