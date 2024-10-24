import json
from typing import List, Union
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, or_, update, desc, and_

from app.init import redis_manager
from app.models.arena_model import Arena, Match
from app.models.datebase import async_session_maker
from app.models.player_model import Player, Fraction
from app.schemas.arena_schemas import ArenaCreateSchema, ArenaBaseSchema, MSGArenaSchema, \
    ArenaRegPlayerSchema, MatchReturnSchema, ArenaDeleteRegPlayerSchema, DeleteRegArenaSchema, StatsArePdaSchema, \
    PlayerInTopSchema, OpenArenaMenuSchema, ActionReturnSchema
from app.service.arena_service import ArenaService, CustomJSONEncoder
from app.service.base_service import get_moscow_time

# arena_queue = []

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
        arena_query = select(Arena).where(Arena.id == arena_id)
        result = await session.execute(arena_query)
        arena_obj = result.scalar_one_or_none()

        if arena_obj is None:
            raise HTTPException(status_code=404, detail="Arena not found")

        for key, value in data.dict().items():
            setattr(arena_obj, key, value)

        await session.commit()
        return arena_obj


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
        return arena_obj


@arena_router.post("/register_arena", summary="Регистрация на Арену")
async def register_arena(data: ArenaRegPlayerSchema) -> ActionReturnSchema:
    async with async_session_maker() as session:
        items = data.items
        cords = {
            "position": data.position,
            "orientation": data.orientation
        }
        player_obj = select(Player).where(Player.steam_id == data.steam_id)
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()

        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        free_areans_obj = select(Arena).where(Arena.free == True)
        free_arenas_stmt = await session.execute(free_areans_obj)
        free_arenas = free_arenas_stmt.scalars().all()

        player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id),
                                               Match.finished == False)
        player_match_stmt = await session.execute(player_match_obj)
        player_match = player_match_stmt.scalar()
        if player_match:
            return ActionReturnSchema(game_data=None, message_data=[MSGArenaSchema(steam_id=player.steam_id,
                                                                                   msg="Вы уже стоите на арене")])

        free_matches_obj = select(Match).where(Match.player2 == None, Match.start == False)
        free_matches_stmt = await session.execute(free_matches_obj)
        free_matches = free_matches_stmt.scalars().all()
        if free_matches:
            match = free_matches[0]
            match.player2 = player.id
            match.old_things_player2 = items
            match.old_cords_player2 = cords

            arena_queue_cache = await redis_manager.get("arena_queue")
            if arena_queue_cache:
                arena_queue = json.loads(arena_queue_cache)
            else:
                arena_queue = []

            if free_arenas:
                if len(arena_queue) == 0:
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
                    return ActionReturnSchema(game_data=[MatchReturnSchema(cords_spawn1=arena.cords_spawn[0],
                                                                           cords_spawn2=arena.cords_spawn[1],
                                                                           player1=steam_id_player1,
                                                                           player2=steam_id_player2,
                                                                           cloths1=match.old_things_player1,
                                                                           cloths2=match.old_things_player2)],
                                              message_data=[MSGArenaSchema(steam_id=player.steam_id,
                                                                           msg="Вы успешно зарегистрированы на арену")])
                else:
                    arena_queue.append(match.id)
                    new_match_list = []
                    for i, free_arena in enumerate(free_arenas):
                        new_match_id = arena_queue.pop(arena_queue[i])
                        new_match_obj = select(Match).where(Match.id == new_match_id)
                        new_match_stmt = await session.execute(new_match_obj)
                        new_match = new_match_stmt.scalar()

                        new_match.arena = free_arena.id
                        new_match.arena_set = free_arena.cloths
                        free_arena.free = False
                        new_match.start = True
                        new_match.time_start = get_moscow_time()

                        steam_id_player1_obj = select(Player).where(Player.id == new_match.player1)
                        steam_id_player1_stmt = await session.execute(steam_id_player1_obj)
                        steam_id_player1 = steam_id_player1_stmt.scalar().steam_id

                        steam_id_player2_obj = select(Player).where(Player.id == new_match.player2)
                        steam_id_player2_stmt = await session.execute(steam_id_player2_obj)
                        steam_id_player2 = steam_id_player2_stmt.scalar().steam_id

                        new_match_list.append(MatchReturnSchema(cords_spawn1=free_arena.cords_spawn[0],
                                                                cords_spawn2=free_arena.cords_spawn[1],
                                                                player1=steam_id_player1,
                                                                player2=steam_id_player2,
                                                                cloths1=new_match.arena_set,
                                                                cloths2=new_match.arena_set))
                        await session.commit()
                    arena_queue_cache = json.dumps(arena_queue)
                    await redis_manager.set("arena_queue", arena_queue_cache)
                    return ActionReturnSchema(game_data=new_match_list,
                                              message_data=[MSGArenaSchema(steam_id=player.steam_id,
                                                                           msg="Вы успешно зарегистрированы на арену")])

            else:
                arena_queue.append(match.id)
                arena_queue_cache = json.dumps(arena_queue)
                await redis_manager.set("arena_queue", arena_queue_cache)
                await session.commit()
                return ActionReturnSchema(game_data=None, message_data=[MSGArenaSchema(steam_id=player.steam_id,
                                                                                        msg="Вы успешно зарегистрированы на арену")])
        else:
            await session.execute(
                insert(Match).values(player1=player.id, old_things_player1=items, old_cords_player1=cords))
            await session.commit()
            return ActionReturnSchema(game_data=None, message_data=[MSGArenaSchema(steam_id=player.steam_id,
                                                                                    msg="Вы успешно зарегистрированы на арену")])


@arena_router.post("/delete_register_arena", summary="Удаление регистрации на Арену")
async def delete_register_arena(data: DeleteRegArenaSchema) -> MSGArenaSchema:
    async with async_session_maker() as session:
        player_obj = select(Player).where(Player.steam_id == data.steam_id)
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()

        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        if player.game_balance < 0:
            raise HTTPException(status_code=400, detail="Недостаточно денег")

        player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id),
                                               Match.finished == False, Match.start == False)
        player_match_stmt = await session.execute(player_match_obj)
        player_match = player_match_stmt.scalar()
        arena_queue_cache = await redis_manager.get("arena_queue")
        arena_queue = json.loads(arena_queue_cache) if arena_queue_cache else []
        if player_match and player_match.id in arena_queue:
            arena_queue.remove(player_match.id)
            arena_queue_cache = json.dumps(arena_queue)
            if player_match.player1 == player.id and player_match.player2:
                player_match.player1 = player_match.player2
                player_match.old_cords_player1 = player_match.old_cords_player2
                player_match.old_things_player1 = player_match.old_things_player2
                player_match.player2 = None
                player_match.old_cords_player2 = None
                player_match.old_things_player2 = None
            elif player_match.player2 == player.id and player_match.player1:
                player_match.player2 = None
                player_match.old_cords_player2 = None
                player_match.old_things_player2 = None
            await session.commit()
            await redis_manager.set("arena_queue", arena_queue_cache)
            return MSGArenaSchema(steam_id=player.steam_id, msg="Вы успешно удалились с арены")
        elif player_match and (not player_match.player2 or not player_match.player1):
            await session.delete(player_match)
            await session.commit()
            return MSGArenaSchema(steam_id=player.steam_id, msg="Вы успешно удалились с арены")
        else:
            return MSGArenaSchema(steam_id=player.steam_id, msg="Вы не стоите в очереди")


async def update_arena_match(session, player1, player2) -> List[MatchReturnSchema]:
    return_list = []
    match_obj = select(Match).where(
        or_(Match.player1 == player1.id, Match.player2 == player1.id),
        or_(Match.player1 == player2.id, Match.player2 == player2.id),
        Match.finished == False, Match.start == True
    )
    match_stmt = await session.execute(match_obj)
    match = match_stmt.scalar()
    if match:
        match_arena_obj = select(Arena).where(Arena.id == match.arena)
        match_arena_stmt = await session.execute(match_arena_obj)
        match_arena = match_arena_stmt.scalar()
        match_arena.free = True
        match.finished = True
        match.time_end = get_moscow_time()
        match.winner = player1.id
        player1.arena_wins += 1
        player2.arena_loses += 1
        player1.kills += 1
        player2.deaths += 1
        player1.arena_rating, player2.arena_rating = ArenaService.calculate_new_ratings(
            player1.arena_rating, player2.arena_rating, 1
        )
        player1.game_balance += int(match_arena.arena_price * 1.5)
        player2.game_balance -= match_arena.arena_price
        await session.commit()
        return_list.append(MatchReturnSchema(
            cords_spawn1=match.old_cords_player1,
            cords_spawn2=match.old_cords_player2,
            player1=player1.steam_id,
            player2=player2.steam_id,
            cloths1=match.old_things_player1,
            cloths2=match.old_things_player2
        ))
        arena_queue_cache = await redis_manager.get("arena_queue")
        arena_queue = json.loads(arena_queue_cache) if arena_queue_cache else []
        if arena_queue:
            new_match_id = arena_queue.pop(0)
            new_match_obj = select(Match).where(Match.id == new_match_id)
            new_match_stmt = await session.execute(new_match_obj)
            new_match = new_match_stmt.scalar()
            new_match.start = True
            new_match.time_start = get_moscow_time()
            new_match.arena_set = match.arena_set
            new_match.arena = match.arena
            match_arena.free = False
            new_player1_obj = select(Player).where(Player.id == new_match.player1)
            new_player1_stmt = await session.execute(new_player1_obj)
            new_player1 = new_player1_stmt.scalar()
            new_player2_obj = select(Player).where(Player.id == new_match.player2)
            new_player2_stmt = await session.execute(new_player2_obj)
            new_player2 = new_player2_stmt.scalar()
            return_list.append(MatchReturnSchema(
                cords_spawn1=new_match.old_cords_player1,
                cords_spawn2=new_match.old_cords_player2,
                player1=new_player1.steam_id,
                player2=new_player2.steam_id,
                cloths1=new_match.old_things_player1,
                cloths2=new_match.old_things_player2
            ))
            await session.commit()
            await redis_manager.set("arena_queue", json.dumps(arena_queue))
    return return_list


@arena_router.get("/stats_arena_pda", summary="Статистика по аренам")
async def stats_arena_pda(steam_id: str = Query(description='Steam ID игрока')) -> StatsArePdaSchema:
    async with async_session_maker() as session:
        player_obj = select(Player).where(Player.steam_id == steam_id)
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()
        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        result = await session.execute(select(Player).order_by(desc(Player.arena_rating)))
        players = result.scalars().all()
        if await redis_manager.get("tops"):
            tops_cache = await redis_manager.get("tops")
            print('Redis get')
            tops = json.loads(tops_cache)
        else:
            tops = []
            for player_top in players:
                player_top_fraction_obj = select(Fraction).where(Fraction.id == player_top.fraction_id)
                player_top_fraction_stmt = await session.execute(player_top_fraction_obj)
                player_top_fraction = player_top_fraction_stmt.scalar()
                if player_top_fraction:
                    fraction = player_top_fraction.name
                else:
                    fraction = "Вольный Сталкер"
                tops.append(PlayerInTopSchema(
                    steam_id=player_top.steam_id,
                    name=player_top.name,
                    surname=player_top.surname,
                    fraction=fraction,
                    vip=player_top.vip,
                    arena_rating=player_top.arena_rating,
                    arena_rang=players.index(player_top) + 1,
                    KD=player_top.kills / player_top.deaths if player_top.deaths != 0 else player_top.kills,
                    win_rate=player_top.arena_wins / (player_top.arena_wins + player_top.arena_loses) * 100
                    if player_top.arena_loses != 0 else 100,
                    max_win_streak=await ArenaService.calculate_max_win_streak(player_top.id, session),
                    matches=player_top.arena_wins + player_top.arena_loses,
                    history_matches=await ArenaService.get_last_10_matches(player_top.id, session)
                ))
            await redis_manager.set("tops", json.dumps(tops, cls=CustomJSONEncoder), expire=3600)
        player_fraction_obj = select(Fraction).where(Fraction.id == player.fraction_id)
        player_fraction_stmt = await session.execute(player_fraction_obj)
        player_fraction = player_fraction_stmt.scalar()
        return StatsArePdaSchema(
            steam_id=player.steam_id,
            name=player.name,
            surname=player.surname,
            fraction=player_fraction.name if player_fraction else 'Вольный Сталкер',
            vip=player.vip,
            arena_rating=player.arena_rating,
            arena_rang=players.index(player) + 1,
            KD=player.kills / player.deaths if player.deaths != 0 else player.kills,
            win_rate=player.arena_wins / (player.arena_wins + player.arena_loses) * 100
            if player.arena_loses != 0 else 100,
            max_win_streak=await ArenaService.calculate_max_win_streak(player.id, session),
            matches=player.arena_wins + player.arena_loses,
            history_matches=await ArenaService.get_last_10_matches(player.id, session),
            tops=tops
        )


@arena_router.get("/open_arena_menu", summary="Открыть меню арены у нпс")
async def open_arena_menu(steam_id: str = Query(description='Steam ID игрока')) -> OpenArenaMenuSchema:
    async with async_session_maker() as session:
        player_obj = select(Player).where(Player.steam_id == steam_id)
        player_stmt = await session.execute(player_obj)
        player = player_stmt.scalar()
        active_player_match_obj = select(Match).where(or_(Match.player1 == player.id, Match.player2 == player.id),
                                                      Match.finished == False)
        active_player_match_stmt = await session.execute(active_player_match_obj)
        active_player_match = active_player_match_stmt.scalar()
        if active_player_match:
            registration_required = False
            if active_player_match.player1 and active_player_match.player2:
                description = None
                arena_queue_cache = await redis_manager.get("arena_queue")
                arena_queue = json.loads(arena_queue_cache) if arena_queue_cache else []
                if active_player_match.id in arena_queue:
                    queue_position = arena_queue.index(active_player_match.id) + 1
                else:
                    queue_position = None

                if player.id == active_player_match.player1:
                    player2_obj = select(Player).where(Player.id == active_player_match.player2)
                    player2_stmt = await session.execute(player2_obj)
                    player2 = player2_stmt.scalar()
                    players = [
                        {
                            "name": f"{player.name}",
                            "surname": f"{player.surname}"
                        },
                        {
                            "name": f"{player2.name}",
                            "surname": f"{player2.surname}"
                        }
                    ]
                else:
                    player1_obj = select(Player).where(Player.id == active_player_match.player1)
                    player1_stmt = await session.execute(player1_obj)
                    player1 = player1_stmt.scalar()
                    players = [
                        {
                            "name": f"{player1.name}",
                            "surname": f"{player1.surname}"
                        },
                        {
                            "name": f"{player.name}",
                            "surname": f"{player.surname}"
                        }
                    ]
            else:
                queue_position = None
                players = None
                description = "Идёт подбор соперника"
        else:
            queue_position = None
            registration_required = True
            players = None
            description = "Вы не зарегистрированы на арену"

        arena_price_obj = select(Arena).where(Arena.free == True)
        arena_price_stmt = await session.execute(arena_price_obj)
        arena_price_instance = arena_price_stmt.scalar()
        if arena_price_instance:
            arena_price = arena_price_instance.arena_price
        else:
            all_arenas = (await session.execute(select(Arena))).scalars().all()
            arena_price = all_arenas[0].arena_price if all_arenas else 0

        return OpenArenaMenuSchema(
            steam_id=player.steam_id,
            registration_required=registration_required,
            queue_position=queue_position,
            players=players,
            description=description,
            arena_price=arena_price
        )