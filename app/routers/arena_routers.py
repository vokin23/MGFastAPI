from typing import List, Union
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, or_, update

from app.models.arena_model import Arena, Match
from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.arena_schemas import ArenaCreateSchema, ArenaBaseSchema, MatchReturnSchema, MSGArenaSchema
from app.service.base_service import get_moscow_time

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


@admin_router.get("/get_arena/{arena_id}", summary="Получение Арены")
async def get_arena(arena_id: int = Query(description='ID Арены')) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        arena = select(Arena).where(Arena.id == arena_id)
        result = await session.execute(arena)
        return result.scalar()


@admin_router.put("/update_arena/{arena_id}", summary="Обновление Арены")
async def update_arena(data: ArenaCreateSchema,
                       arena_id: int = Query(description='ID Арены')) -> ArenaBaseSchema:
    async with async_session_maker() as session:
        arena = select(Arena).where(Arena.id == arena_id)
        arena_obj = await session.execute(arena)
        arena_obj.scalar().update(data.model_dump())
        await session.commit()
        return arena_obj.scalar()


@admin_router.patch("/patch_arena/{arena_id}", summary="Обновление Арены")
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


@admin_router.delete("/delete_arena/{arena_id}", summary="Удаление Арены")
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

        # Получаем все матчи, где нет одного из игроков
        free_matches_objs = select(Match).where(Match.start == False, Match.finished == False,
                                                Match.player1 == None or Match.player2 == None)
        free_matches = await session.execute(free_matches_objs)
        free_matches = free_matches.scalars().all()

        if free_matches:
            match = free_matches[0]
            if not match.player1:
                await session.execute(update(Match).where(Match.id == match.id).values(player1=player.id, old_things_player1=player.cloths))
            else:
                await session.execute(update(Match).where(Match.id == match.id).values(player2=player.id, old_things_player2=player.cloths))
            await session.commit()
        else:
            new_match_obj = insert(Match).values(player1=player.id,
                                                 old_things_player1=player.cloths,
                                                 time_created=get_moscow_time()
                                                 ).returning(Match)
            new_match_stmt = await session.execute(new_match_obj)
            new_match = new_match_stmt.scalar()
            await session.commit()
            arena_queue.append(new_match.id)

        free_arenas_objs = select(Arena).where(Arena.free == True)
        free_arenas = await session.execute(free_arenas_objs)
        free_arenas = free_arenas.scalars().all()

        new_start_matches = []
        for free_arena in free_arenas:
            match = arena_queue.pop(0)
            await session.execute(update(Match).where(Match.id == match).values(arena=free_arena.id, start=True, time_start=get_moscow_time()))
            await session.commit()
            new_start_matches.append(MatchReturnSchema(cords_spawn=free_arena.cords_spawn,
                                                       player1=match.player1,
                                                       player2=match.player2,
                                                       cloths_player1=match.old_things_player1,
                                                       cloths_player2=match.old_things_player2))
        return new_start_matches if new_start_matches else [None]


@arena_router.post("/update_arena_match", summary="Обновить\завершить матч")
async def update_arena_match(data: dict) -> List[MatchReturnSchema]:
    async with async_session_maker() as session:
        return []