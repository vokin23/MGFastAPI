from sqlalchemy import select, update, insert

from app.models.arena_model import Match, Arena
from app.schemas.arena_schemas import MatchReturnSchema
from app.service.base_service import get_moscow_time


class ArenaService:

    @staticmethod
    async def check_free_matches_or_create_new(session, arena_queue, player):
        # Получаем все матчи, где нет одного из игроков
        free_matches_objs = select(Match).where(Match.start == False, Match.finished == False,
                                                Match.player1 == None or Match.player2 == None)
        free_matches = await session.execute(free_matches_objs)
        free_matches = free_matches.scalars().all()

        if free_matches:
            match = free_matches[0]
            if not match.player1:
                await session.execute(update(Match).where(Match.id == match.id).values(player1=player.id,
                                                                                       old_things_player1=player.cloths))
            else:
                await session.execute(update(Match).where(Match.id == match.id).values(player2=player.id,
                                                                                       old_things_player2=player.cloths))
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

    @staticmethod
    async def if_free_arena_start_matches(session, arena_queue):
        free_arenas_objs = select(Arena).where(Arena.free == True)
        free_arenas = await session.execute(free_arenas_objs)
        free_arenas = free_arenas.scalars().all()

        new_start_matches = []
        if free_arenas:
            for free_arena in free_arenas:
                match = arena_queue.pop(0)
                await session.execute(update(Match).where(Match.id == match).values(arena=free_arena.id, start=True,
                                                                                    time_start=get_moscow_time()))
                await session.commit()
                new_start_matches.append(MatchReturnSchema(cords_spawn=free_arena.cords_spawn,
                                                           player1=match.player1,
                                                           player2=match.player2,
                                                           cloths_player1=match.old_things_player1,
                                                           cloths_player2=match.old_things_player2))
        return new_start_matches if new_start_matches else [None]
