import random

from sqlalchemy import select, update, insert, or_

from app.models.arena_model import Match, Arena
from app.schemas.arena_schemas import MatchReturnSchema
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