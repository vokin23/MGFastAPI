import random
from datetime import datetime, timedelta
from typing import List

import pytz
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.orm import selectinload
from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.quest_model import ReputationType, Operator, Quest, Activity, QuestType, GameNameAnimal
from app.schemas.quest_schemas import ReputationTypeCreateSchema, ReputationTypeBaseSchema, OperatorCreateSchema, \
    OperatorBaseSchema, QuestBaseSchema, QuestCreateSchema, MSGSchema, PDAInfoSchema, ActivityBaseSchema, \
    UpdateActivitySchema
from app.service.quest_service import QuestService

quest_router = APIRouter(prefix="/quest")
admin_router = APIRouter()


@admin_router.post("/create_reputation_type", summary="Создание типа репутации")
async def create_reputation_type(data: ReputationTypeCreateSchema) -> ReputationTypeBaseSchema:
    async with async_session_maker() as session:
        add_reputation_type = insert(ReputationType).values(**data.model_dump()).returning(ReputationType)
        result = await session.execute(add_reputation_type)
        reputation_type = result.scalar()
        await session.commit()
        return reputation_type


@admin_router.put("/update_reputation_type", summary="Обновление типа репутации")
async def put_reputation_type(data: ReputationTypeCreateSchema,
                              reputation_type_id: int = Query(
                                  description="ID Типа репутации")) -> ReputationTypeBaseSchema:
    async with async_session_maker() as session:
        update_reputation_type = update(ReputationType).where(ReputationType.id == reputation_type_id).values(
            **data.model_dump()).returning(ReputationType)
        result = await session.execute(update_reputation_type)
        reputation_type = result.scalar()
        await session.commit()
        return reputation_type


@admin_router.get("/get_reputation_type", summary="Получение типа репутации")
async def get_reputation_type(
        reputation_type_id: int = Query(description="ID Типа репутаwии")) -> ReputationTypeBaseSchema:
    async with async_session_maker() as session:
        reputation_type_obj = select(ReputationType).where(ReputationType.id == reputation_type_id)
        result = await session.execute(reputation_type_obj)
        reputation_type = result.scalar()
        if reputation_type is None:
            raise HTTPException(status_code=404, detail="Тип репутации не найден")
        return reputation_type


@admin_router.get("/get_reputation_types", summary="Получение всех типов репутации")
async def get_all_reputation_types() -> List[ReputationTypeBaseSchema]:
    async with async_session_maker() as session:
        get_reputation_types = select(ReputationType)
        result = await session.execute(get_reputation_types)
        reputation_types = result.scalars().all()
        return reputation_types


@admin_router.delete("/delete_reputation_type", summary="Удаление типа репутации")
async def delete_reputation_type(
        reputation_type_id: int = Query(description="ID Типа репутации")) -> ReputationTypeBaseSchema:
    async with async_session_maker() as session:
        get_reputation_type = select(ReputationType).where(ReputationType.id == reputation_type_id)
        result = await session.execute(get_reputation_type)
        reputation_type = result.scalar()
        if reputation_type is None:
            raise HTTPException(status_code=404, detail="Тип репутации не найден")
        await session.delete(reputation_type)
        await session.commit()
        return reputation_type


@admin_router.post("/create_operator", summary="Cоздание оператора")
async def create_operator(data: OperatorCreateSchema) -> OperatorBaseSchema:
    async with async_session_maker() as session:
        add_operator = insert(Operator).values(**data.model_dump()).returning(Operator)
        result = await session.execute(add_operator)
        operator = result.scalar()
        await session.commit()
        return operator


@admin_router.get("/get_operator", summary="Получение оператора")
async def get_operator(operator_id: int = Query(description="ID Оператора")) -> OperatorBaseSchema:
    async with async_session_maker() as session:
        operator_obj = select(Operator).where(Operator.id == operator_id)
        result = await session.execute(operator_obj)
        operator = result.scalar()
        if operator is None:
            raise HTTPException(status_code=404, detail="Оператор не найден")
        return operator


@admin_router.get("/get_operators", summary="Получение всех операторов")
async def get_all_operators() -> List[OperatorBaseSchema]:
    async with async_session_maker() as session:
        get_operators = select(Operator)
        result = await session.execute(get_operators)
        operators = result.scalars().all()
        return operators


@admin_router.put("/update_operator", summary="Обновление оператора")
async def put_operator(data: OperatorCreateSchema,
                       operator_id: int = Query(description="ID Оператора")) -> OperatorBaseSchema:
    async with async_session_maker() as session:
        update_operator = update(Operator).where(Operator.id == operator_id).values(**data.model_dump()).returning(
            Operator)
        result = await session.execute(update_operator)
        operator = result.scalar()
        await session.commit()
        return operator


@admin_router.delete("/delete_operator", summary="Удаление оператора")
async def delete_operator(operator_id: int = Query(description="ID Оператора")):
    async with async_session_maker() as session:
        get_operator = select(Operator).where(Operator.id == operator_id)
        result = await session.execute(get_operator)
        operator = result.scalar()
        if operator is None:
            raise HTTPException(status_code=404, detail="Оператор не найден")
        await session.delete(operator)
        await session.commit()
        return {"message": "Оператор удален"}


@admin_router.post("/create_quest", summary="Создание квеста")
async def create_quest(data: QuestCreateSchema) -> QuestBaseSchema:
    async with async_session_maker() as session:
        add_quest = insert(Quest).values(**data.model_dump()).returning(Quest)
        result = await session.execute(add_quest)
        quest = result.scalar()
        await session.commit()
        return quest


@admin_router.get("/get_quest", summary="Получение квеста")
async def get_quest(quest_id: int = Query(description="ID Квеста")) -> QuestBaseSchema:
    async with async_session_maker() as session:
        quest_obj = select(Quest).where(Quest.id == quest_id)
        result = await session.execute(quest_obj)
        quest = result.scalar()
        if quest is None:
            raise HTTPException(status_code=404, detail="Квест не найден")
        return quest


@admin_router.get("/get_quests", summary="Получение всех квестов")
async def get_all_quests() -> List[QuestBaseSchema]:
    async with async_session_maker() as session:
        get_quests = select(Quest)
        result = await session.execute(get_quests)
        quests = result.scalars().all()
        return quests


@admin_router.put("/update_quest", summary="Обновление квеста")
async def put_quest(data: QuestCreateSchema, quest_id: int = Query(description="ID Квеста")) -> QuestBaseSchema:
    async with async_session_maker() as session:
        update_quest = update(Quest).where(Quest.id == quest_id).values(**data.model_dump()).returning(Quest)
        result = await session.execute(update_quest)
        quest = result.scalar()
        await session.commit()
        return quest


@admin_router.delete("/delete_quest", summary="Удаление квеста")
async def delete_quest(quest_id: int = Query(description="ID Квеста")):
    async with async_session_maker() as session:
        get_quest = select(Quest).where(Quest.id == quest_id)
        result = await session.execute(get_quest)
        quest = result.scalar()
        if quest is None:
            raise HTTPException(status_code=404, detail="Квест не найден")
        await session.delete(quest)
        await session.commit()
        return {"message": "Квест удален"}


@quest_router.post("/create_activiti", summary="Создание активности игрока")
async def create_activity(steam_id: str, quest_id: int) -> MSGSchema:
    async with async_session_maker() as session:
        request_data = {
            "steam_id": steam_id,
            "msg": ""
        }
        # Получаем игрока по steam_id
        player_obj = select(Player).where(Player.steam_id == steam_id)
        player_result = await session.execute(player_obj)
        player = player_result.scalar()

        # Получаем квест по quest_id
        quest_obj = select(Quest).where(Quest.id == quest_id)
        quest_result = await session.execute(quest_obj)
        quest = quest_result.scalar()

        # Получаем оператора
        operator_obj = select(Operator).where(Operator.id == quest.operator_id)
        operator_result = await session.execute(operator_obj)
        operator = operator_result.scalar()

        # Получаем reputation_type
        reputation_type_obj = select(ReputationType).where(ReputationType.id == operator.reputation_type_id)
        reputation_type_result = await session.execute(reputation_type_obj)
        reputation_type = reputation_type_result.scalar()

        player_reputation = None
        for reputation in player.reputation:
            if reputation["name"] == reputation_type.name:
                player_reputation = reputation["level"]
                break

        result = await QuestService.quest_check(player, quest, session, request_data, player_reputation)
        if result:
            return result

        new_activity = insert(Activity).values(player_id=player.id,
                                               quest_id=quest.id,
                                               conditions=quest.conditions,
                                               is_active=True,
                                               is_completed=False,
                                               award_take=False,
                                               changed_at=datetime.now()).returning(
            Activity)
        await session.execute(new_activity)
        await session.commit()
        request_data["msg"] = f"Квест {quest.title} принят!"
        return MSGSchema(**request_data)


@quest_router.get("/get_available_quests", summary="Получение квестов, доступных игроку")
async def get_available_quests(steam_id: str = Query(description='SteamID игрока'),
                               operator_id: int = Query(description='ID оператора')) -> List[QuestBaseSchema]:
    async with async_session_maker() as session:
        # Получаем игрока по steam_id
        player = await QuestService.get_player_by_steam_id(session, steam_id)

        # Получаем оператора с квестами
        operator_obj = select(Operator).options(selectinload(Operator.quests)).where(Operator.id == operator_id)
        operator_result = await session.execute(operator_obj)
        operator = operator_result.scalar()

        # Получаем reputation_type
        reputation_type_obj = select(ReputationType).where(ReputationType.id == operator.reputation_type_id)
        reputation_type_result = await session.execute(reputation_type_obj)
        reputation_type = reputation_type_result.scalar()

        # Получаем активности игрока
        player_activities = await QuestService.get_active_activities(session, player.id)

        # Получаем список id квестов, которые уже выполняются игроком и составляем черный список квестов
        quests_id = [quest.id for quest in operator.quests]
        quest_black_list = []
        for activity in player_activities:
            if activity.quest_id in quests_id:
                quest_black_list.append(activity.quest_id)

        # Получаем репутацию игрока
        player_reputation = None
        for reputation in player.reputation:
            if reputation["name"] == reputation_type.name:
                player_reputation = reputation["level"]
                break

        # Получаем доступные квесты
        available_quests = []
        for quest in operator.quests:
            if quest.reputation_need <= player_reputation and quest.id not in quest_black_list:
                available_quests.append(quest)
        return available_quests


@quest_router.get("/get_info_pda", summary="Получение информации для PDA")
async def get_info_pda(steam_id: str = Query(description='SteamID игрока')) -> PDAInfoSchema:
    async with async_session_maker() as session:
        # Получаем игрока по steam_id
        player = await QuestService.get_player_by_steam_id(session, steam_id)
        # Получаем активные активности игрока
        player_activities = await QuestService.get_active_activities(session, player.id)
        # Convert activities to ActivityBaseSchema
        activities = [ActivityBaseSchema.from_orm(activity) for activity in player_activities]
        await QuestService.refactoring_conditions(session, activities)
        # Получаем репутацию игрока
        player_reputation = player.reputation
        responce_data = {
            "steam_id": steam_id,
            "activities": activities,
            "reputation": player_reputation,
            "vip_lvl": QuestService.get_str_vip_name(player.vip_lvl)
        }
        return PDAInfoSchema(**responce_data)


@quest_router.post("/update_activity_player", summary="Обновляет активность игрока по квестам")
async def update_activity_player(data: dict) -> MSGSchema:
    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, data.get('Player').get('steamID'))
        active_activities = await QuestService.get_active_activities(session, player.id)
        activity_type = data.get("activityType")
        response_data = {
            "steam_id": player.steam_id,
            "msg": ""
        }

        if activity_type in ["MG_Activity_ZombieKillHandler", "MG_Activity_AnimalKillHandler"]:
            game_name_animal_class_name = data.get("ZombieData").get(
                "typeName") if activity_type == "MG_Activity_ZombieKillHandler" else data.get("AnimalData").get(
                "typeName")
            game_name_animal_obj = select(GameNameAnimal).where(
                GameNameAnimal.class_name == game_name_animal_class_name)
            game_name_animal_result = await session.execute(game_name_animal_obj)
            game_name_animal = game_name_animal_result.scalar()
            if not game_name_animal:
                game_name_animal_obj = insert(GameNameAnimal).values(name='', class_name=game_name_animal_class_name)
                await session.execute(game_name_animal_obj)
                await session.commit()
            for active_activity in active_activities:
                check_completed = False
                for condition in active_activity.conditions:
                    if game_name_animal_class_name == condition.condition_name:
                        condition.progress = str(int(condition.progress) + 1)
                        if int(condition.progress) >= int(condition.need):
                            check_completed = True
                active_activity.is_completed = check_completed  # Обновляем атрибут объекта напрямую
                await session.merge(active_activity)  # SQLAlchemy сама выполнит UPDATE запрос
            await session.commit()  # Commit after all activities are updated
            for active_activity in active_activities:
                if active_activity.is_completed:
                    response_data["msg"] = f"Квест {await active_activity.quest.title} выполнен!"
                    return MSGSchema(**response_data)

        elif activity_type in ["ActionOpenStashCase", "ActionSkinning"]:
            for active_activity in active_activities:
                check_completed = True
                for condition in active_activity.conditions:
                    if activity_type == condition.get("condition_name"):
                        condition["progress"] = str(int(condition.get("progress")) + 1)
                        if int(condition.get("progress")) > int(condition.get("need")):
                            check_completed = False
                active_activity.is_completed = check_completed
                session.add(active_activity)  # Add the modified activity back to the session
            await session.commit()  # Commit after all activities are updated
            for active_activity in active_activities:
                if active_activity.is_completed:
                    response_data["msg"] = f"Квест {await active_activity.quest.title} выполнен!"
                    return MSGSchema(**response_data)

        elif activity_type == "DistanceActivity":
            for active_activity in active_activities:
                check_completed = True
                for condition in active_activity.conditions:
                    if activity_type == condition.get("condition_name"):
                        condition["progress"] = str(int(condition.get("progress")) + int(data['distance']))
                        if int(condition.get("progress")) > int(condition.get("need")):
                            check_completed = False
                active_activity.is_completed = check_completed
                session.add(active_activity)  # Add the modified activity back to the session
            await session.commit()  # Commit after all activities are updated
            for active_activity in active_activities:
                if active_activity.is_completed:
                    response_data["msg"] = f"Квест {await active_activity.quest.title} выполнен!"
                    return MSGSchema(**response_data)

        return MSGSchema(**response_data)
