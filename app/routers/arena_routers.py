from typing import List, Union
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, or_, update

from app.models.arena_model import Arena, Match
from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.arena_schemas import ArenaCreateSchema, ArenaBaseSchema, MatchReturnSchema, MSGArenaSchema
from app.service.arena_service import ArenaService


arena_queue = []

arena_router = APIRouter(prefix="/arena")
admin_router = APIRouter(prefix="/arena")


@admin_router.post("/create_arena", summary="Создание Арены")
async def create_arena(data: ArenaCreateSchema) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        new_arena_obj = insert(Arena).values(**data.model_dump()).returning(Arena)
        result = await session.execute(new_arena_obj)
        await session.commit()
        return result.scalar()


@admin_router.get("/get_arenas", summary="Получение Арен")
async def get_arenas() -> List[ArenaBaseSchema]:
    async with async_session_maker() as session:
        arenas = select(Arena)
        result = await session.execute(arenas)
        return result.scalars().all()


@admin_router.get("/get_arena", summary="Получение Арены")
async def get_arena(arena_id: int = Query(description='ID Арены')) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        arena = select(Arena).where(Arena.id == arena_id)
        result = await session.execute(arena)
        return result.scalar()


@admin_router.put("/update_arena", summary="Обновление Арены")
async def update_arena(data: ArenaCreateSchema,
                       arena_id: int = Query(description='ID Арены')) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        arena = select(Arena).where(Arena.id == arena_id)
        arena_obj = await session.execute(arena)
        arena_obj.scalar().update(data.model_dump())
        await session.commit()
        return arena_obj.scalar()


@admin_router.patch("/patch_arena", summary="Обновление Арены")
async def patch_arena(data: ArenaCreateSchema,
                      arena_id: int = Query(description='ID Арены')) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        arena = select(Arena).where(Arena.id == arena_id)
        arena_obj = await session.execute(arena)
        arena_instance = arena_obj.scalar()

        # Обновляем только непустые поля
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(arena_instance, field, value)

        await session.commit()
        return arena_instance


@admin_router.delete("/delete_arena", summary="Удаление Арены")
async def delete_arena(arena_id: int = Query(description='ID Арены')) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        arena = select(Arena).where(Arena.id == arena_id)
        arena_obj = await session.execute(arena)
        await session.delete(arena_obj.scalar())
        await session.commit()
        return arena_obj.scalar()


@arena_router.post("/register_arena", summary="Регистрация на Арену")
async def register_arena(data: dict) -> List[Union[MatchReturnSchema, MSGArenaSchema]]:
    async with async_session_maker() as session:
        player_obj = select(Player).where(Player.steam_id == data.get('steam_id'))
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()

        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id), Match.finished == False)
        player_match_stmt = await session.execute(player_match_obj)
        player_match = player_match_stmt.scalar()
        if player_match and player_match.id in arena_queue:
            return [MSGArenaSchema(steam_id=player.steam_id, msg="Вы уже зарегистрированы на арену")]

        await ArenaService.check_free_matches_or_create_new(session, arena_queue, player)
        await ArenaService.if_free_arena_start_matches(session, arena_queue)


@arena_router.post("/delete_register_arena", summary="Удаление регистрации на Арену")
async def delete_register_arena(data: dict) -> MSGArenaSchema:
    async with async_session_maker() as session:
        player_obj = select(Player).where(Player.steam_id == data.get('steam_id'))
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()

        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id), Match.finished == False)
        player_match_stmt = await session.execute(player_match_obj)
        player_match = player_match_stmt.scalar()
        if player_match and player_match.id in arena_queue:
            arena_queue.remove(player_match.id)
            return MSGArenaSchema(steam_id=player.steam_id, msg="Вы успешно удалились с арены")


#TODO: Доработать метод обновления матча и создать вывод информации для КПК
@arena_router.post("/update_arena_match", summary="Обновить\завершить матч")
async def update_arena_match(data: dict) -> List[MatchReturnSchema]:
    async with async_session_maker() as session:
        return []
