from datetime import datetime, timedelta
from typing import List

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType, GameNameAnimal, Action, BoostReputationVip


class QuestService:
    moscow_tz = pytz.timezone('Europe/Moscow')

