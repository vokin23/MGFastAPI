import random
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.secret_stash_models import Stash, StashCategory
from app.schemas.secret_stash_schemas import SecretStashSchema, SecretStashCreateSchema, SecretStashOpenSchema, \
    SecretStashCategoryCreate, SecretStashCategorySchema, SecretStashPatch, SecretStashCategoryPatch
from app.service.secret_stash_service import SecretStashService

stashes_router = APIRouter(prefix="/stashes")
admin_router = APIRouter()


@stashes_router.get("/get_stashes", summary="Получение списка Stash'ей")
async def get_all_stashes() -> List[SecretStashSchema]:
    async with async_session_maker() as session:
        stashes = await session.execute(select(Stash))
        stash_list = stashes.scalars().all()
        for stash in stash_list:
            if stash.is_opened:
                stash.is_opened = False
        await session.commit()
        return stash_list


@admin_router.post("/create_stash", summary="Создание нового Stash'а")
async def create_stash(stash_data: SecretStashCreateSchema) -> SecretStashSchema:
    async with async_session_maker() as session:
        new_stash_stmt = insert(Stash).values(**stash_data.dict()).returning(Stash)
        result = await session.execute(new_stash_stmt)
        await session.commit()
        new_stash = result.scalar_one()
        return new_stash


@admin_router.put("/put_stash/", summary="Полное обновление Stash'а")
async def put_stash(stash_data: SecretStashCategoryCreate, stash_id: int = Query(description="ID Stash'а")) -> SecretStashSchema:
    async with async_session_maker() as session:
        stash = await session.execute(select(Stash).where(Stash.id == stash_id))
        stash = stash.scalar_one_or_none()
        if stash is None:
            raise HTTPException(status_code=404, detail="Stash not found")
        for key, value in stash_data.dict().items():
            if value is not None:
                setattr(stash, key, value)
        await session.commit()
    return stash


@admin_router.patch("/update_stash/", summary="Обновление информации о Stash'е")
async def update_stash(stash_data: SecretStashPatch, stash_id: int = Query(description="ID Stash'а")) -> SecretStashSchema:
    async with async_session_maker() as session:
        stash = await session.execute(select(Stash).where(Stash.id == stash_id))
        stash = stash.scalar_one_or_none()
        if stash is None:
            raise HTTPException(status_code=404, detail="Stash not found")
        for key, value in stash_data.dict().items():
            if value is not None:
                setattr(stash, key, value)
        await session.commit()
    return stash


@admin_router.delete("/delete_stash/", summary="Удаление Stash'а")
async def delete_stash(stash_id: int = Query(description="ID Stash'а")) -> SecretStashSchema:
    async with async_session_maker() as session:
        stash = await session.execute(select(Stash).where(Stash.id == stash_id))
        stash = stash.scalar_one_or_none()
        if stash is None:
            raise HTTPException(status_code=404, detail="Stash not found")
        await session.delete(stash)
        await session.commit()
    return stash


@stashes_router.post("/open", summary="Открытие Stash'а")
async def open_stash(stash_id: int = Query(), steam_id: str = Query()) -> SecretStashOpenSchema:
    async with async_session_maker() as session:
        stash = await session.execute(select(Stash).where(Stash.id == stash_id))
        stash = stash.scalar_one_or_none()
        player_obj = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = player_obj.scalar_one_or_none()
        if stash is None:
            raise HTTPException(status_code=404, detail="Stash not found")
        if stash.is_opened:
            return SecretStashOpenSchema(steam_id=steam_id, msg="Похоже, что схрон уже открыли до вас", awards=[])
        else:
            if player.vip_lvl == 4:
                return await SecretStashService.open_stash(session, stash, steam_id)
            elif player.vip_lvl == 3 and random.randint(0, 100) > 25:
                return await SecretStashService.open_stash(session, stash, steam_id)
            elif player.vip_lvl == 2 and random.randint(0, 100) > 50:
                return await SecretStashService.open_stash(session, stash, steam_id)
            elif player.vip_lvl in [0, 1] and random.randint(0, 100) > 65:
                return await SecretStashService.open_stash(session, stash, steam_id)
            response_data = {
                "steam_id": steam_id,
                "msg": "К сожалению, вы не смогли открыть схрон! Попробуйте еще раз!",
                "awards": []
            }
    return SecretStashOpenSchema(**response_data)


@admin_router.post("/crate_category", summary="Создание новой категории Stash'ей")
async def create_category(category_data: SecretStashCategoryCreate) -> SecretStashCategorySchema:
    async with async_session_maker() as session:
        new_category_stmt = insert(StashCategory).values(**category_data.dict()).returning(StashCategory)
        result = await session.execute(new_category_stmt)
        await session.commit()
        new_category = result.scalar_one()
        return new_category


@admin_router.get("/get_categories", summary="Получение списка категорий Stash'ей")
async def get_all_categories() -> List[SecretStashCategorySchema]:
    async with async_session_maker() as session:
        categories = await session.execute(select(StashCategory))
        return categories.scalars().all()


@admin_router.patch("/update_category/", summary="Обновление информации о категории Stash'ей")
async def update_category(category_data: SecretStashCategoryPatch,
                          category_id: int = Query(..., description="ID категории")) -> SecretStashCategorySchema:
    async with async_session_maker() as session:
        category = await session.execute(select(StashCategory).where(StashCategory.id == category_id))
        category = category.scalar_one_or_none()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        for key, value in category_data.dict().items():
            if value is not None:
                setattr(category, key, value)
        await session.commit()
    return category


@admin_router.put("/put_category/", summary="Полное обновление категории Stash'ей")
async def put_category(category_data: SecretStashCategoryCreate,
                       category_id: int = Query(..., description="ID категории")) -> SecretStashCategorySchema:
    async with async_session_maker() as session:
        category = await session.execute(select(StashCategory).where(StashCategory.id == category_id))
        category = category.scalar_one_or_none()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        for key, value in category_data.dict().items():
            if value is not None:
                setattr(category, key, value)
        await session.commit()
    return category


@admin_router.delete("/delete_category/", summary="Удаление категории Stash'ей")
async def delete_category(category_id: int = Query(description='id Категории')) -> SecretStashCategorySchema:
    async with async_session_maker() as session:
        category = await session.execute(select(StashCategory).where(StashCategory.id == category_id))
        category = category.scalar_one_or_none()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        await session.delete(category)
        await session.commit()
    return category
