from datetime import datetime, timedelta
from typing import List

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm.attributes import flag_modified

from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType, GameNameAnimal, Action, \
    BoostReputationVip, QuestType
from app.schemas.quest_schemas import MSGSchema


class QuestService:
    moscow_tz = pytz.timezone('Europe/Moscow')

    @classmethod
    async def quest_check(cls, player: Player, quest: Quest, session: AsyncSession, request_data: dict,
                          player_reputation):
        moscow_tz = pytz.timezone('Europe/Moscow')
        current_date_naive = datetime.now(moscow_tz).replace(tzinfo=None)
        # Получаем все активные активности игрока
        last_activiti = []

        activities_obj = await session.execute(
            select(Activity).where(Activity.player_id == player.id, Activity.is_active == True)
        )
        activities = activities_obj.scalars().all()

        if quest.id in [activiti.quest_id for activiti in activities]:
            request_data["msg"] = "Вы выполняете этот квест!"
            return MSGSchema(**request_data)

        if quest.type == QuestType.daily:
            last_activities_obj = await session.execute(
                select(Activity)
                .join(Quest, Activity.quest_id == Quest.id)
                .where(Quest.type == quest.type, Activity.player_id == player.id,
                       Activity.changed_at == current_date_naive.date())
            )
            last_activiti = last_activities_obj.scalars().all()
        elif quest.type == QuestType.weekly:
            last_activities_obj = await session.execute(
                select(Activity)
                .join(Quest, Activity.quest_id == Quest.id)
                .where(Quest.type == quest.type, Activity.player_id == player.id,
                       Activity.changed_at >= current_date_naive - timedelta(days=7))
            )
            last_activiti = last_activities_obj.scalars().all()
        elif quest.type == QuestType.monthly:
            last_activities_obj = await session.execute(
                select(Activity)
                .join(Quest, Activity.quest_id == Quest.id)
                .where(Quest.type == quest.type, Activity.player_id == player.id,
                       Activity.changed_at >= current_date_naive - timedelta(days=30))
            )
            last_activiti = last_activities_obj.scalars().all()
        elif quest.type == QuestType.lore:
            active_lore_obj = await session.execute(
                select(Activity)
                .join(Quest, Activity.quest_id == Quest.id)
                .where(Quest.type == quest.type, Activity.is_active == True)
            )
            active_lore = active_lore_obj.scalars().all()
            if len(active_lore) >= 1:
                request_data["msg"] = "У вас уже есть активный квест лор!"
                return MSGSchema(**request_data)

        if last_activiti:
            if len(last_activiti) == 1:
                last_activiti = last_activiti[0:1]
            else:
                last_activiti = last_activiti[0:2]
        else:
            last_activiti = []

        # Получаем активные активности с таким же типом квеста
        activities_obj = await session.execute(
            select(Activity)
            .join(Activity.quest)
            .where(Quest.type == quest.type, Activity.is_active == True)
        )
        activities_type = activities_obj.scalars().all()

        if player.vip and player.vip_lvl == 4:
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
                request_data[
                    "msg"] = "У вас уже 5 активных квестов!\n Выполните их прежде чем принимать новые или получите статус ЛЕГЕНДА!"
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

    @staticmethod
    async def get_active_activities(session: AsyncSession, player_id: int):
        activities_obj = await session.execute(
            select(Activity)
            .where(Activity.player_id == player_id, Activity.is_active == True)
        )
        activities = activities_obj.scalars().all()
        return activities

    @staticmethod
    async def get_active_activities_not_complete(session: AsyncSession, player_id: int):
        activities_obj = await session.execute(
            select(Activity)
            .where(Activity.player_id == player_id, Activity.is_active == True, Activity.is_completed == False)
        )
        activities = activities_obj.scalars().all()
        return activities

    @staticmethod
    async def get_player_by_steam_id(session: AsyncSession, steam_id: str):
        player_obj = await session.execute(
            select(Player)
            .where(Player.steam_id == steam_id)
        )
        player = player_obj.scalar()
        return player

    @staticmethod
    def get_str_vip_name(vip_lvl: int):
        vip_levels = ['Новичок', 'Опытный', 'Ветеран', 'Мастер', 'Легенда']
        return vip_levels[vip_lvl] if vip_lvl < len(vip_levels) else 'Неизвестно'

    @staticmethod
    async def refactoring_conditions(session: AsyncSession, activities):
        for activity in activities:
            new_conditions = []
            for condition in activity.conditions:
                condition_name = condition.condition_name
                result = await session.execute(
                    select(GameNameAnimal).where(GameNameAnimal.class_name == condition_name))
                game_name_animal = result.scalar()
                if game_name_animal:
                    condition.condition_name = game_name_animal.name
                new_conditions.append(condition)
            activity.conditions = new_conditions

    @staticmethod
    async def update_activity_by_distance(active_activities, distance):
        """Обновляет активность по условиям, связанным с пройденным расстоянием."""
        for active_activity in active_activities:
            check_completed = True
            for condition in active_activity.conditions:
                if condition["condition_name"] == "DistanceActivity":
                    condition["progress"] = str(int(condition["progress"]) + int(distance))
                    if int(condition["progress"]) >= int(condition["need"]):
                        condition["progress"] = condition["need"]
                        check_completed = False
            active_activity.is_completed = check_completed

    @staticmethod
    async def update_activity_by_kill_animal(session, data, activity_type, active_activities):
        """Обновляет активность по условиям, связанным с убийством животных."""

        game_name_animal_class_name = data.get("ZombieData").get(
            "typeName") if activity_type == "MG_Activity_ZombieKillHandler" else data.get("AnimalData").get(
            "typeName")
        game_name_animal_display_name = data.get("ZombieData").get(
            "displayName") if activity_type == "MG_Activity_ZombieKillHandler" else data.get("AnimalData").get(
            "displayName")
        game_name_animal_obj = select(GameNameAnimal).where(
            GameNameAnimal.class_name == game_name_animal_class_name)
        game_name_animal_result = await session.execute(game_name_animal_obj)
        game_name_animal = game_name_animal_result.scalar()
        if not game_name_animal:
            game_name_animal_obj = insert(GameNameAnimal).values(name=game_name_animal_display_name,
                                                                 class_name=game_name_animal_class_name)
            await session.execute(game_name_animal_obj)

        for active_activity in active_activities:
            check_completed = False
            for condition in active_activity.conditions:
                if game_name_animal_class_name == condition["condition_name"]:
                    if int(condition["progress"]) < int(condition["need"]):
                        condition["progress"] = str(int(condition["progress"]) + 1)
                    if int(condition["progress"]) >= int(condition["need"]):
                        check_completed = True
            active_activity.is_completed = check_completed
            flag_modified(active_activity, "conditions")

    @staticmethod
    async def update_activity_by_stash_or_skinning(activity_type, active_activities):
        """Обновляет активность по условиям, связанным со сбором ресурсов."""

        for active_activity in active_activities:
            check_completed = True
            for condition in active_activity.conditions:
                if activity_type == condition["condition_name"]:
                    condition["progress"] = str(int(condition["progress"]) + 1)
                    if int(condition["progress"]) >= int(condition["need"]):
                        check_completed = False
            active_activity.is_completed = check_completed
            flag_modified(active_activity, "conditions")
