import random

from sqlalchemy import select, update, insert, or_, desc

from app.models import Player
from app.models.arena_model import Match, Arena
from app.models.datebase import async_session_maker_null_pool
from app.schemas.arena_schemas import MatchReturnSchema, HistoryMatchSchema, HistoryPlayerSchema
from app.service.base_service import get_moscow_time


class ArenaService:
    @staticmethod
    def calculate_new_ratings(rating_a, rating_b, result_a, k=32):
        """
        Calculate new ratings for two players after a match.

        :param rating_a: Current rating of player A
        :param rating_b: Current rating of player B
        :param result_a: Result of player A (1 for win, 0 for loss)
        :param k: K-factor (default is 32)
        :return: New ratings for player A and player B
        """
        # Calculate expected scores
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

        # Calculate new ratings
        new_rating_a = rating_a + k * (result_a - expected_a)
        new_rating_b = rating_b + k * ((1 - result_a) - expected_b)

        # Ensure ratings are not less than 0
        new_rating_a = max(0, new_rating_a)
        new_rating_b = max(0, new_rating_b)

        return new_rating_a, new_rating_b

    @staticmethod
    async def calculate_max_win_streak(player_id: int, session) -> int:
        # Получаем все матчи игрока
        matches = await session.execute(
            select(Match).where(or_(Match.player1 == player_id, Match.player2 == player_id)).order_by(
                Match.time_start)
        )
        matches = matches.scalars().all()

        max_streak = 0
        current_streak = 0

        for match in matches:
            if match.winner == player_id:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    @staticmethod
    async def get_last_10_matches(player_id: int, session):
        result = await session.execute(
            select(Match)
            .where(or_(Match.player1 == player_id, Match.player2 == player_id))
            .order_by(desc(Match.time_start))
            .limit(10)
        )
        matches = result.scalars().all()

        history_matches = []
        for match in matches:
            player1 = await session.get(Player, match.player1)
            player2 = await session.get(Player, match.player2)
            player1 = HistoryPlayerSchema(
                steam_id=player1.steam_id,
                name=player1.name,
                surname=player1.surname,
                fraction=player1.fraction_name
            )
            player2 = HistoryPlayerSchema(
                steam_id=player2.steam_id,
                name=player2.name,
                surname=player2.surname,
                fraction=player2.fraction_name
            )
            history_match = HistoryMatchSchema(
                players=[player1, player2],
                winner=match.winner
            )
            history_matches.append(history_match)

        return history_matches
