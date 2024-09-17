import random
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.secret_stash_models import Stash, StashCategory
from app.schemas.secret_stash_schemas import SecretStashSchema, SecretStashCreateSchema, SecretStashOpenSchema, \
    SecretStashCategoryCreate, SecretStashCategorySchema, SecretStashPatch, SecretStashCategoryPatch

stashes_router = APIRouter(prefix="/stashes")


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


@stashes_router.post("/admin/create_stash", summary="Создание нового Stash'а")
async def create_stash(stash_data: SecretStashCreateSchema) -> SecretStashSchema:
    async with async_session_maker() as session:
        new_stash_stmt = insert(Stash).values(**stash_data.dict()).returning(Stash)
        result = await session.execute(new_stash_stmt)
        await session.commit()
        new_stash = result.scalar_one()
        return new_stash


@stashes_router.put("/admin/put_stash/", summary="Полное обновление Stash'а")
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


@stashes_router.patch("/admin/update_stash/", summary="Обновление информации о Stash'е")
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


@stashes_router.delete("/admin/delete_stash/", summary="Удаление Stash'а")
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
        if stash is None:
            raise HTTPException(status_code=404, detail="Stash not found")
        if stash.is_opened:
            return SecretStashOpenSchema(steam_id=steam_id, msg="Похоже, что схрон уже открыли до вас", awards=[])
        else:
            stash.is_opened = True
            stmt_category = await session.execute(select(StashCategory).where(StashCategory.id == stash.category_id))
            category = stmt_category.scalar_one()
            awards_list = category.awards_list
            awards = random.choice(awards_list)
            award_response = []
            for award in awards.keys():
                award_response.append({
                    "class_name": award,
                    "value": awards[award]
                })

            response_data = {
                "steam_id": steam_id,
                "msg": "Поздравляем! Вы открыли схрон и получили награду",
                "awards": award_response
            }
        await session.commit()
    return SecretStashOpenSchema(**response_data)


@stashes_router.post("/admin/crate_category", summary="Создание новой категории Stash'ей")
async def create_category(category_data: SecretStashCategoryCreate) -> SecretStashCategorySchema:
    async with async_session_maker() as session:
        new_category_stmt = insert(StashCategory).values(**category_data.dict()).returning(StashCategory)
        result = await session.execute(new_category_stmt)
        await session.commit()
        new_category = result.scalar_one()
        return new_category


@stashes_router.get("/admin/get_categories", summary="Получение списка категорий Stash'ей")
async def get_all_categories() -> List[SecretStashCategorySchema]:
    async with async_session_maker() as session:
        categories = await session.execute(select(StashCategory))
        return categories.scalars().all()


@stashes_router.patch("/admin/update_category/", summary="Обновление информации о категории Stash'ей")
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


@stashes_router.put("/admin/put_category/", summary="Полное обновление категории Stash'ей")
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


@stashes_router.delete("/admin/delete_category/", summary="Удаление категории Stash'ей")
async def delete_category(category_id: int = Query(description='id Категории')) -> SecretStashCategorySchema:
    async with async_session_maker() as session:
        category = await session.execute(select(StashCategory).where(StashCategory.id == category_id))
        category = category.scalar_one_or_none()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        await session.delete(category)
        await session.commit()
    return category
