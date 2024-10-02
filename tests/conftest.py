import pytest

from app.config import settings
from app.models.datebase import Base, engine_null_pool
from app.main import app
from app.models import *
from app.service.base_service import read_json_async
from httpx import AsyncClient

data_url = 'tests/data/'
base_url = 'http://127.0.0.1:8000/'


@pytest.fixture(scope="session", autouse=True)
def test_check_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def test_setup_database(test_check_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def test_register_reputation_type(test_setup_database):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        data = await read_json_async(data_url + 'reputation_type.json')
        for reputation_type in data:
            await ac.post(
                "/v1/admin/quest/create_reputation_type",
                json=reputation_type
            )


@pytest.fixture(scope="session", autouse=True)
async def test_register_player(test_register_reputation_type):
    async with AsyncClient(app=app, base_url=base_url) as ac:
        data = await read_json_async(data_url + 'steam_ids.json')
        for steam_id in data:
            await ac.post(
                "/v1/player/",
                params={"steam_id": steam_id}
            )
