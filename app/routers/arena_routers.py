from typing import List, Union
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, or_, update

from app.models.arena_model import Arena, Match
from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.arena_schemas import ArenaCreateSchema, ArenaBaseSchema, MSGArenaSchema, \
    ArenaRegPlayerSchema, MatchReturnSchema
from app.service.arena_service import ArenaService
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
async def register_arena(data: ArenaRegPlayerSchema) -> List[Union[MatchReturnSchema, MSGArenaSchema]]:
    async with async_session_maker() as session:
        items = data.items
        cords = [data.position, data.orientation]
        player_obj = select(Player).where(Player.steam_id == data.steam_id)
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()

        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        free_areans_obj = select(Arena).where(Arena.free == True)
        free_arenas_stmt = await session.execute(free_areans_obj)
        free_arenas = free_arenas_stmt.scalars().all()

        player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id),
                                               Match.finished == False, Match.start == False)
        player_match_stmt = await session.execute(player_match_obj)
        player_match = player_match_stmt.scalar()
        if player_match:
            return [MSGArenaSchema(steam_id=player.steam_id, msg="Вы уже зарегистрированы на арену")]

        free_matches_obj = select(Match).where(Match.player2 == None, Match.start == False)
        free_matches_stmt = await session.execute(free_matches_obj)
        free_matches = free_matches_stmt.scalars().all()
        if free_matches:
            match = free_matches[0]
            match.player2 = player.id
            match.old_things_player2 = items
            match.old_cords_player2 = cords
            if free_arenas: # Добавить обработку очереди
                arena = free_arenas[0]
                match.arena = arena.id
                match.arena_set = free_arenas[0].cloths  # Сделать рандомный выбор сета
                free_arenas[0].free = False
                match.start = True
                match.time_start = get_moscow_time()
                await session.commit()
                steam_id_player1_obj = select(Player).where(Player.id == match.player1)
                steam_id_player1_stmt = await session.execute(steam_id_player1_obj)
                steam_id_player1 = steam_id_player1_stmt.scalar().steam_id
                steam_id_player2 = player.steam_id
                return [MatchReturnSchema(cords_spawn=arena.cords_spawn, player1=steam_id_player1,
                                          player2=steam_id_player2, cloths=match.arena_set,
                                          )]
            else:
                arena_queue.append(match.id)
                await session.commit()
                return [MSGArenaSchema(steam_id=player.steam_id, msg="Вы успешно зарегистрированы на арену")]
        else:
            await session.execute(
                insert(Match).values(player1=player.id, old_things_player1=items, old_cords_player1=cords))
            await session.commit()
            return [MSGArenaSchema(steam_id=player.steam_id, msg="Вы успешно зарегистрированы на арену")]


@arena_router.post("/delete_register_arena", summary="Удаление регистрации на Арену")
async def delete_register_arena(data: ArenaRegPlayerSchema) -> MSGArenaSchema:
    async with async_session_maker() as session:
        player_obj = select(Player).where(Player.steam_id == data.steam_id)
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()

        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id),
                                               Match.finished == False)
        player_match_stmt = await session.execute(player_match_obj)
        player_match = player_match_stmt.scalar()
        if player_match and player_match.id in arena_queue:
            arena_queue.remove(player_match.id)
            return MSGArenaSchema(steam_id=player.steam_id, msg="Вы успешно удалились с арены")


# TODO: Доработать метод обновления матча и создать вывод информации для КПК
@arena_router.post("/update_arena_match", summary="Обновить\завершить матч")
async def update_arena_match(data: dict) -> List[MatchReturnSchema]:
    async with async_session_maker() as session:
        return []
