from typing import List

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType, GameNameAnimal, Action


class QuestService:
    moscow_tz = pytz.timezone('Europe/Moscow')

    @staticmethod
    async def get_player_by_steam_id(session: AsyncSession, steam_id: int) -> Player:
        player = await session.execute(select(Player).where(Player.steam_id == steam_id))
        return player.scalar_one_or_none()

    @staticmethod
    async def get_active_activities_by_player_id(session: AsyncSession, player_id: int) -> List[Activity]:
        activities = await session.execute(select(Activity).where(Activity.player == player_id))
        return activities.scalars().all()

    @staticmethod
    async def get_operator_by_id(session: AsyncSession, operator_id: int) -> Operator:
        operator = await session.execute(select(Operator).where(Operator.id == operator_id))
        return operator.scalar_one_or_none()

    @staticmethod
    async def get_quests_by_operator_id(session: AsyncSession, operator_id: int) -> List[Quest]:
        quests = await session.execute(select(Quest).where(Quest.operator_id == operator_id))
        return quests.scalars().all()

    @staticmethod
    async def refactor_condition(session: AsyncSession, quest: Quest):
        conditions = quest.conditions
        quest.conditions = []
        for condition_key, progress in conditions.items():
            if not quest.requiredItems:
                if await session.execute(select(GameNameAnimal).where(
                        GameNameAnimal.class_name == condition_key)).scalar_one_or_none():
                    quest.conditions.append({
                        "condition_name": f'Убить {GameNameAnimal.name}',
                        "progress": str(progress)
                    })
                elif condition_key == "DistanceActivity":
                    quest.conditions.append({
                        "condition_name": 'Пройти метров',
                        "progress": str(progress)
                    })
                elif condition_key == "ActionOpenStashCase":
                    quest.conditions.append({
                        "condition_name": 'Открыть тайников',
                        "progress": str(progress)
                    })
                elif condition_key == "ActionSkinning":
                    quest.conditions.append({
                        "condition_name": 'Разделать туш',
                        "progress": str(progress)
                    })
                else:
                    action = await session.execute(
                        select(Action).where(Action.name == condition_key)).scalar_one_or_none()
                    quest.conditions.append({
                        "condition_name": action.description,
                        "progress": str(progress)
                    })
            else:
                quest.conditions.append({
                    "condition_name": condition_key,
                    "progress": str(progress)
                })

    @staticmethod
    async def get_activity_by_id(session: AsyncSession, quest_id: int) -> Activity:
        activity = await session.execute(select(Activity).where(Activity.id == quest_id))
        return activity.scalar_one_or_none()

    @staticmethod
    async def update_reputation(quest: Quest):
        for operator in reputation.reputation.keys():
            if operator == quest.operator.name:
                reputation.reputation[operator] += quest.reputation_add
            else:
                reputation.reputation[operator] -= quest.reputation_minus

    @staticmethod
    async def update_activity(activity: Activity):
        activity.award = True
        activity.is_completed = True
        activity.is_active = False