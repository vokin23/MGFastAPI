from datetime import datetime, timedelta
from typing import List

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType, GameNameAnimal, Action, BoostReputationVip
from app.schemas.quest_schemas import MSGSchema


class QuestService:
    moscow_tz = pytz.timezone('Europe/Moscow')

    @classmethod
    async def quest_check(cls, player: Player, quest: Quest, session: AsyncSession, request_data: dict, player_reputation):
        # Получаем все активные активности игрока

        if quest.type == "daily":
            last_activities_obj = await session.execute(
                select(Activity).where(Activity.quest.type == quest.type, Activity.player_id == player.id, Activity.changed_at == datetime.now(cls.moscow_tz).date())
            )
            last_activiti = last_activities_obj.scalars()[0:2]
        elif quest.type == "weekly":
            last_activities_obj = await session.execute(
                select(Activity).where(Activity.quest.type == quest.type, Activity.player_id == player.id, Activity.changed_at >= datetime.now(cls.moscow_tz) - timedelta(days=7))
            )
            last_activiti = last_activities_obj.scalars()[0:2]
        elif quest.type == "monthly":
            last_activities_obj = await session.execute(
                select(Activity).where(Activity.quest.type == quest.type, Activity.player_id == player.id, Activity.changed_at >= datetime.now(cls.moscow_tz) - timedelta(days=30))
            )
            last_activiti = last_activities_obj.scalars()[0:2]
        elif quest.type == "lore":
            active_lore_obj = await session.execute(
                select(Activity).where(Activity.quest.type == quest.type, Activity.is_active == True)
            )
            active_lore = active_lore_obj.scalars().all()
            if len(active_lore) >= 1:
                request_data["msg"] = "У вас уже есть активный квест лор!"
                return MSGSchema(**request_data)


        activities_obj = await session.execute(
            select(Activity).where(Activity.player_id == player.id, Activity.is_active == True)
        )
        activities = activities_obj.scalars().all()

        # Получаем активные активности с таким же типом квеста
        activities_obj = await session.execute(
            select(Activity).where(Activity.quest.type == quest.type, Activity.is_active == True)
        )
        activities_type = activities_obj.scalars().all()

        if player.vip and player.vip_level == 4:
            if len(activities) >= 6:
                request_data["msg"] = "У вас уже 6 активных квестов!\n Выполните их прежде чем принимать новые!"
                return MSGSchema(**request_data)
            elif len(activities_type) >= 2:
                request_data[
                    "msg"] = f"У вас уже 2 активных квеста типа {quest.type}!\n Выполните их прежде чем принимать новые!"
                return MSGSchema(**request_data)
            elif len(activities) == 5 and player_reputation < 2000:
                request_data[
                    "msg"] = "У вас уже 5 активных квестов!\n Выполните их прежде чем принимать новые или наберите 2000 репутации!"
                return MSGSchema(**request_data)
            if last_activiti and len(last_activiti) == 2:
                request_data["msg"] = f"Вы уже выполнили сегодня 2 квеста типа {quest.type}!"
                return MSGSchema(**request_data)
        else:
            if len(activities) == 5:
                request_data["msg"] = "У вас уже 5 активных квестов!\n Выполните их прежде чем принимать новые или получите статус ЛЕГЕНДА!"
                return MSGSchema(**request_data)
            elif len(activities) == 4 and player_reputation < 2000:
                request_data[
                    "msg"] = "У вас уже 4 активных квеста!\n Выполните их прежде чем принимать новые или наберите 2000 репутации!"
                return MSGSchema(**request_data)
            elif len(activities_type) >= 2 and player_reputation > 2000:
                request_data[
                    "msg"] = f"У вас уже 2 активных квеста типа {quest.type}!\n Выполните их прежде чем принимать новые!"
                return MSGSchema(**request_data)
            elif len(activities_type) >= 1 and player_reputation < 2000:
                request_data[
                    "msg"] = f"У вас уже 1 активный квест типа {quest.type}!\n Выполните его прежде чем принимать новыеили наберите 2000 репутации!"
                return MSGSchema(**request_data)
