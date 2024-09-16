import random
from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, update

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.quest_model import ReputationType, Operator, Quest, Activity
from app.schemas.quest_schemas import *

quest_router = APIRouter(prefix="/quest")


@quest_router.post("/create_reputation_type", summary="Создание вида репутации")
async def create_reputation_type(reputation_type: ReputationTypeCreate) -> ReputationTypeCreate:
    async with async_session_maker() as session:
        new_reputation_type = await session.execute(insert(ReputationType).values(**reputation_type.dict()).returning(ReputationType))
        await session.commit()
        return new_reputation_type


@quest_router.get("/get_reputation_types", summary="Получение видов репутации")
async def get_reputation_types() -> List[ReputationTypeBase]:
    async with async_session_maker() as session:
        result = await session.execute(select(ReputationType))
        return result.scalars().all()


@quest_router.patch("/update_reputation_type/", summary="Обновление вида репутации")
async def patch_reputation_type(reputation_type_data: ReputationTypePatch,
                                 reputation_type_id: int = Query(description='ID типа репктации')) -> ReputationTypeBase:
    async with async_session_maker() as session:
        reputation_type = select(ReputationType).where(ReputationType.id == reputation_type_id)
        reputation_type = await session.execute(reputation_type)
        reputation_type = reputation_type.scalar_one_or_none()
        if reputation_type is None:
            raise HTTPException(status_code=404, detail="Reputation type not found")
        for key, value in reputation_type_data.dict().items():
            if value is not None:
                setattr(reputation_type, key, value)
        await session.commit()
        return reputation_type


@quest_router.delete("/delete_reputation_type/", summary="Удаление вида репутации")
async def delete_reputation_type(reputation_type_id: int = Query(description='ID типа репктации')) -> str:
    async with async_session_maker() as session:
        reputation_type = select(ReputationType).where(ReputationType.id == reputation_type_id)
        reputation_type = await session.execute(reputation_type)
        reputation_type = reputation_type.scalar_one_or_none()
        if reputation_type is None:
            raise HTTPException(status_code=404, detail="Reputation type not found")
        await session.delete(reputation_type)
        await session.commit()
        return f"Reputation type with id {reputation_type_id} deleted"


@quest_router.post("/create_operator", summary="Создание оператора квеста")
async def create_operator(operator: OperatorCreate) -> OperatorBase:
    async with async_session_maker() as session:
        new_operator = await session.execute(insert(Operator).values(**operator.dict()).returning(Operator))
        await session.commit()
        return new_operator


@quest_router.get("/get_operators", summary="Получение операторов квестов")
async def get_operators() -> List[OperatorBase]:
    async with async_session_maker() as session:
        result = await session.execute(select(Operator))
        return result.scalars().all()


@quest_router.patch("/update_operator/", summary="Обновление оператора квеста")
async def patch_operator(operator_data: OperatorPatch,
                          operator_id: int = Query(description='ID оператора квеста')) -> OperatorBase:
    async with async_session_maker() as session:
        operator = select(Operator).where(Operator.id == operator_id)
        operator = await session.execute(operator)
        operator = operator.scalar_one_or_none()
        if operator is None:
            raise HTTPException(status_code=404, detail="Operator not found")
        for key, value in operator_data.dict().items():
            if value is not None:
                setattr(operator, key, value)
        await session.commit()
        return operator


@quest_router.delete("/delete_operator/", summary="Удаление оператора квеста")
async def delete_operator(operator_id: int = Query(description='ID оператора квеста')) -> str:
    async with async_session_maker() as session:
        operator = select(Operator).where(Operator.id == operator_id)
        operator = await session.execute(operator)
        operator = operator.scalar_one_or_none()
        if operator is None:
            raise HTTPException(status_code=404, detail="Operator not found")
        await session.delete(operator)
        await session.commit()
        return f"Operator with id {operator_id} deleted"


@quest_router.post("/create_quest", summary="Создание квеста")
async def create_quest(quest: QuestCreate) -> QuestBase:
    async with async_session_maker() as session:
        new_quest = await session.execute(insert(Quest).values(**quest.dict()).returning(Quest))
        await session.commit()
        return new_quest


@quest_router.get("/get_quests", summary="Получение квестов")
async def get_quests() -> List[QuestBase]:
    async with async_session_maker() as session:
        result = await session.execute(select(Quest))
        return result.scalars().all()


@quest_router.patch("/update_quest/", summary="Обновление квеста")
async def patch_quest(quest_data: QuestPatch,
                        quest_id: int = Query(description='ID квеста')) -> QuestBase:
        async with async_session_maker() as session:
            quest = select(Quest).where(Quest.id == quest_id)
            quest = await session.execute(quest)
            quest = quest.scalar_one_or_none()
            if quest is None:
                raise HTTPException(status_code=404, detail="Quest not found")
            for key, value in quest_data.dict().items():
                if value is not None:
                    setattr(quest, key, value)
            await session.commit()
            return quest


@quest_router.delete("/delete_quest/", summary="Удаление квеста")
async def delete_quest(quest_id: int = Query(description='ID квеста')) -> str:
    async with async_session_maker() as session:
        quest = select(Quest).where(Quest.id == quest_id)
        quest = await session.execute(quest)
        quest = quest.scalar_one_or_none()
        if quest is None:
            raise HTTPException(status_code=404, detail="Quest not found")
        await session.delete(quest)
        await session.commit()
        return f"Quest with id {quest_id} deleted"


@quest_router.get("/get_quest_activity_from_player", summary="Получение квеста по игрока steam_id")
async def get_quest_activity_from_player(steam_id: int = Query(description='Steam ID игрока')) -> List[ActivityBase]:
    async with async_session_maker() as session:
        player = select(Player).where(Player.steam_id == steam_id)
        player = await session.execute(player)
        player = player.scalar_one_or_none()
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        result = await session.execute(select(Activity).where(Activity.player == player.id,
                                                              Activity.is_active == True,
                                                              Activity.is_completed == False))
        return result.scalars().all()


#TODO: Доделать метод
@quest_router.get("/get_quest_available_to_the_player", summary="Получение доступных квестов для игрока")
async def get_quest_available_to_the_player(steam_id: int = Query(description='Steam ID игрока'),
                                            operator_id: int = Query(description='ID оператора')) -> QuestResponseForPlayer:
    async with async_session_maker() as session:
        player = select(Player).where(Player.steam_id == steam_id)
        player = await session.execute(player)
        player = player.scalar_one_or_none()
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        operator = select(Operator).where(Operator.id == operator_id)
        operator = await session.execute(operator)
        operator = operator.scalar_one_or_none()
        if operator is None:
            raise HTTPException(status_code=404, detail="Operator not found")
        activity_quests = await session.execute(select(Activity).where(Activity.player == player.id,
                                                                      Activity.is_active == True))
        activity_quests = activity_quests.scalars().all()
        activity_quests_lore = [activity.quest for activity in activity_quests if activity.quest.type == 'lore']

