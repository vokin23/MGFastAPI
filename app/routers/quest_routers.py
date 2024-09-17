import random
from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert, update

from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.models.quest_model import ReputationType, Operator, Quest, Activity
from app.schemas.quest_schemas import ReputationTypeBase, ReputationTypeCreate, ReputationTypePatch, \
    OperatorCreate, OperatorBase, OperatorPatch, QuestBase, QuestCreate, QuestPatch, QuestCompletionResponse, \
    ActivityBase, ActivityCreate, PDASchema
from app.service.quest_service import QuestService

quest_router = APIRouter(prefix="/quest")


@quest_router.post("/admin/create_reputation_type", summary="Создание вида репутации")
async def create_reputation_type(reputation_type: ReputationTypeCreate) -> ReputationTypeBase:
    async with async_session_maker() as session:
        new_reputation_type = await session.execute(
            insert(ReputationType).values(**reputation_type.dict()).returning(ReputationType))
        await session.commit()
        return new_reputation_type.scalar_one()


@quest_router.get("/admin/get_reputation_types", summary="Получение видов репутации")
async def get_reputation_types() -> List[ReputationTypeBase]:
    async with async_session_maker() as session:
        result = await session.execute(select(ReputationType))
        return result.scalars().all()


@quest_router.patch("/admin/update_reputation_type/", summary="Обновление вида репутации")
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


@quest_router.delete("/admin/delete_reputation_type/", summary="Удаление вида репутации")
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


@quest_router.post("/admin/create_operator", summary="Создание оператора квеста")
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


@quest_router.patch("/admin/update_operator/", summary="Обновление оператора квеста")
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


@quest_router.delete("/admin/delete_operator/", summary="Удаление оператора квеста")
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


@quest_router.post("/admin/create_quest", summary="Создание квеста")
async def create_quest(quest: QuestCreate) -> QuestBase:
    async with async_session_maker() as session:
        new_quest = await session.execute(insert(Quest).values(**quest.dict()).returning(Quest))
        await session.commit()
        return new_quest


@quest_router.get("/admin/get_quests", summary="Получение квестов")
async def get_quests() -> List[QuestBase]:
    async with async_session_maker() as session:
        result = await session.execute(select(Quest))
        return result.scalars().all()


@quest_router.patch("/admin/update_quest/", summary="Обновление квеста")
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


@quest_router.delete("/admin/delete_quest/", summary="Удаление квеста")
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


@quest_router.get("/get_quest_activity_from_player", summary="Получение квестов игрока по steam_id.")
async def get_quest_activity_from_player(steam_id: int = Query(description='Steam ID игрока')) -> List[ActivityBase]:
    async with async_session_maker() as session:
        player_obj = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = player_obj.scalar_one_or_none()
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        activities = await session.execute(
            select(Activity).where(Activity.player == player.id, Activity.is_active == True))
        return activities.scalars().all()


@quest_router.post("/completing_the_quest", summary="Завершает активность квеста игрока")
async def completing_the_quest(steam_id: str = Query(description='Steam ID игрока'),
                               activity_id: int = Query(description='ID активности')) -> QuestCompletionResponse:
    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, steam_id)
        activity = await QuestService.get_activity_by_id(session, activity_id)
        quest = await QuestService.get_quest_by_id(session, activity.quest)
        awards_list = quest.awards
        if quest.required_items or activity.is_completed:
            await QuestService.update_reputation(session, player, quest, activity)
            return QuestCompletionResponse(steam_id=steam_id,
                                           msg=f"Поздравляем с завершением квеста {quest.title}",
                                           awards=awards_list)
        else:
            raise HTTPException(status_code=400, detail="Quest not completed")


@quest_router.post("/update_activity_user", summary="Обновление активности игрока по квестам")
async def update_activity_user(data: dict) -> ActivityCreate:
    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, data['steam_id'])
        activitys_stmt = await session.execute(select(Activity).where(Activity.player == player.id,
                                                                      Activity.is_active == True,
                                                                      Activity.is_completed == False))
        activitys = activitys_stmt.scalars().all()
        activity_type = data['activityType']
        updated_activitys = await QuestService.update_game_activity_player(session, activitys, activity_type)
        return updated_activitys


@quest_router.post("/create_activity", summary="Создание активности игрока по квесту")
async def create_activity(steam_id: str = Query(description='Steam ID игрока'),
                          quest_id: int = Query(description='ID квеста')) -> ActivityCreate:
    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, steam_id)
        quest = await QuestService.get_quest_by_id(session, quest_id)
        if await QuestService.check_player_activity(session, player, quest):
            return await QuestService.check_player_activity(session, player, quest)
        insert(Activity).values(player=player.id, quest=quest.id, is_active=True).returning(Activity)
        response_data = {
            "steam_id": player.steam_id,
            "msg": 'Квест принят'
        }
        return ActivityCreate(**response_data)


@quest_router.get("/get_quest_available_to_the_player", summary="Получение доступных квестов для игрока")
async def get_quest_available_to_the_player(steam_id: str = Query(description='Steam ID игрока'),
                                            operator_id: int = Query(description='ID оператора')) -> List[QuestBase]:
    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, steam_id)
        operator = await QuestService.get_operator_by_id(session, operator_id)
        activity = await QuestService.get_activity_by_player(session, player)
        quests = await QuestService.get_quests_by_operator(session, operator)

        activity_quests_lore = []
        activity_quests = []
        response_list = []
        for act in activity:
            quest_id = act.quest
            quest = await QuestService.get_quest_by_id(session, quest_id)
            if quest.type == 'lore':
                activity_quests_lore.append(quest.id)
            if act.is_active:
                activity_quests.append(quest.id)

        for quest in quests:
            if quest.id not in activity_quests and quest.id not in activity_quests_lore:
                response_list.append(quest)
        return response_list


@quest_router.get('/get_info_pda', summary='Получение информации для PDA')
async def get_info_pda(steam_id: str = Query(description='Steam ID игрока')) -> PDASchema:
    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, steam_id)
        activity = await QuestService.get_activity_by_player(session, player)
        req_conditions_list = []
        for act in activity:
            quest_id = act.quest
            quest = await QuestService.get_quest_by_id(session, quest_id)
            if quest.required_items:
                for req in quest.required_items:
                    req_conditions_list.append(
                        {
                            "condition_name": req["classname"],
                            "progress": req["count"]
                        }
                    )
        if req_conditions_list:
            activity.conditions = req_conditions_list
        data_reputations = []
        for reputation, level in player.reputation.items():
            data_reputations.append(
                {
                    "name": reputation,
                    "level": level
                }
            )

        response = {
            "steam_id": player.steam_id,
            "activity": activity,
            "reputation": data_reputations,
            "vip": player.vip_lvl
        }
        return PDASchema(**response)
