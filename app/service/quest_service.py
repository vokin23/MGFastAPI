import pytz

from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType

class QuestService:
    moscow_tz = pytz.timezone('Europe/Moscow')
