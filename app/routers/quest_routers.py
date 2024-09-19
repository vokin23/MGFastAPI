import random
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, update

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.quest_model import ReputationType, Operator, Quest, Activity
from app.schemas.quest_schemas import ReputationTypeCreateSchema, ReputationTypeBaseSchema, OperatorCreateSchema, \
    OperatorBaseSchema, QuestBaseSchema, QuestCreateSchema, MSGSchema

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

        # Получаем все активности игрока
        activities_player_obj = select(Activity).where(Activity.player_id == player.id)
        activities_player_result = await session.execute(activities_player_obj)
        activities_player = activities_player_result.scalars().all()

        # Проверяем, что у игрока не более 6 активных квестов
        len_active_activities_quest = len([activity for activity in activities_player if activity.is_active])
        activities_quest = [activity for activity in activities_player]
        for activity_quest in activities_quest:
            if activity_quest == quest and activity_quest.is_active:
                request_data["msg"] = f"Вы уже выполняете этот квест!"
                return MSGSchema(**request_data)
            elif activity_quest == quest and activity_quest.type == "lore":
                request_data["msg"] = f"Вы уже выполнили этот лорный квест!"
                return MSGSchema(**request_data)
            elif activity_quest == quest and activity_quest.type == "daily" and activity_quest.changed_at.date() >= datetime.now().date() - timedelta(
                    days=1):
                request_data[
                    "msg"] = f"Вы уже выполнили дневной квест!\nПопробуйте принять квест {activity_quest.changed_at.date() + timedelta(days=1)} числа!!"
                return MSGSchema(**request_data)
            elif activity_quest == quest and activity_quest.type == "weekly" and activity_quest.changed_at.date() >= datetime.now().date() - timedelta(
                    days=7):
                request_data[
                    "msg"] = f"Вы уже выполнили недельный квест!\nПопробуйте принять квест {activity_quest.changed_at.date() + timedelta(days=7)} числа!!"
                return MSGSchema(**request_data)
            elif activity_quest == quest and activity_quest.type == "monthly" and activity_quest.changed_at.date() >= datetime.now().date() - timedelta(
                    days=30):
                request_data[
                    "msg"] = f"Вы уже выполнили месячный квест!\nПопробуйте принять квест {activity_quest.changed_at.date() + timedelta(days=30)} числа!!"
                return MSGSchema(**request_data)
            elif activity_quest == quest and len_active_activities_quest >= 4:
                if player.vip_lvl <= 3 and player.reputation[quest.operator.reputation_type.name] < 2000:
                    request_data["msg"] = (f"У вас уже есть 4 активных квеста!\n"
                                           f"Выполните хотя бы один из них, чтобы принять новый или прокачайте репутацию и VIP статус!")
                    return MSGSchema(**request_data)
                elif player.vip_lvl == 4 and player.reputation[quest.operator.reputation_type.name] < 2000 and len_active_activities_quest >= 5:
                    request_data["msg"] = (f"У вас уже есть 5 активных квестов!\n"
                                           f"Выполните хотя бы один из них, чтобы принять новый или прокачайте репутацию!")
                    return MSGSchema(**request_data)
                elif player.vip_lvl == 4 and player.reputation[quest.operator.reputation_type.name] >= 2000 and len_active_activities_quest >= 6:
                    request_data["msg"] = (f"У вас уже есть 6 активных квестов!\n"
                                           f"Выполните хотя бы один из них, чтобы принять новый!")
                    return MSGSchema(**request_data)

        new_activity = Activity(player_id=player.id, quest_id=quest.id, conditions=quest.conditions)
        await session.add(new_activity)
        await session.commit()
        request_data["msg"] = f"Квест {quest.title} принят!"
        return MSGSchema(**request_data)