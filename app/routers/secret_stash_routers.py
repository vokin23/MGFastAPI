from typing import List

from fastapi import APIRouter, Query
from app.models.datebase import async_session_maker
from app.repositories.secret_stash_repository import StashRepository, StashCategoryRepository
from app.schemas.secret_stash_schemas import SecretStashSchema, SecretStashCreateSchema, SecretStashOpenSchema, \
    SecretStashCategoryCreate

stashes_router = APIRouter(prefix="/stashes")


@stashes_router.get("/get_stashes", summary="Получение списка Stash'ей")
async def get_all_stashes() -> List[SecretStashSchema]:
    async with async_session_maker() as session:
        return await StashRepository(session).get_all()


@stashes_router.post("/create_stash", summary="Создание нового Stash'а")
async def create_stash(stash_data: SecretStashCreateSchema):
    async with async_session_maker() as session:
        stash = await StashRepository(session).add(stash_data)
        await session.commit()
    return {"status": "OK", "data": stash}


@stashes_router.post("/open", summary="Открытие Stash'а")
async def open_stash(stash_id: int = Query(), steam_id: str = Query()) -> SecretStashOpenSchema:
    async with async_session_maker() as session:
        return await StashRepository(session).open_stash(stash_id, steam_id)


@stashes_router.post("/crate_category", summary="Создание новой категории Stash'ей")
async def create_category(category_data: SecretStashCategoryCreate):
    async with async_session_maker() as session:
        category = await StashCategoryRepository(session).add(category_data)
        await session.commit()
    return {"status": "OK", "data": category}
