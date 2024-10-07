import random

from sqlalchemy import select, update, insert, or_

from app.models.arena_model import Match, Arena
from app.schemas.arena_schemas import MatchReturnSchema
from app.service.base_service import get_moscow_time


class ArenaService:
    pass