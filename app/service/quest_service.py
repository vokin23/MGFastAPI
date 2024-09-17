from typing import List

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType, GameNameAnimal, Action, BoostReputationVip


class QuestService:
    moscow_tz = pytz.timezone('Europe/Moscow')

    @staticmethod
    async def get_player_by_steam_id(session: AsyncSession, steam_id: str) -> Player:
        result = await session.execute(select(Player).where(Player.steam_id == steam_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_quest_by_id(session: AsyncSession, quest_id: int) -> Quest:
        result = await session.execute(select(Quest).where(Quest.id == quest_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_activity_by_id(session: AsyncSession, activity_id: int) -> Activity:
        result = await session.execute(select(Activity).where(Activity.id == activity_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_operator_by_quest(session: AsyncSession, quest: Quest) -> Operator:
        result = await session.execute(select(Operator).where(Operator.id == quest.operator))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_reputation_type_by_id(session: AsyncSession, id: id) -> ReputationType:
        result = await session.execute(select(ReputationType).where(ReputationType.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_reputation_types(session: AsyncSession) -> List[ReputationType]:
        result = await session.execute(select(ReputationType))
        return result.scalars().all()

    @staticmethod
    async def update_reputation(session: AsyncSession, player: Player, quest: Quest, activity: Activity):
        operator = await QuestService.get_operator_by_quest(session, quest)
        operator_reputation_type = await QuestService.get_reputation_type_by_id(session, operator.reputation_type)

        if quest.required_items or activity.is_completed:
            activity.award = True
            activity.is_completed = True
            activity.is_active = False
            if player.vip:
                boost = await session.execute(select(BoostReputationVip).where(BoostReputationVip.level == player.vip_lvl))
                player.reputation[operator_reputation_type.name] += quest.reputation_add + boost.scalar_one().boost_value
            else:
                player.reputation[operator_reputation_type.name] += quest.reputation_add
                reputation_types = await QuestService.get_all_reputation_types(session)
                for reputation_type in reputation_types:
                    if reputation_type.name in player.reputation and reputation_type.name != operator_reputation_type.name and not reputation_type.static:
                        player.reputation[reputation_type.name] -= quest.reputation_minus
        await session.commit()
