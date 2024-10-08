from fastapi import APIRouter

from app.models.datebase import async_session_maker
from app.routers.arena_routers import update_arena_match
from app.service.quest_service import QuestService
from app.routers.quest_routers import update_activity_player

action_router = APIRouter(prefix="/action")


@action_router.post("/action", summary='Метод для обработки активностей игроков')
async def action_update_or_create(data: dict):

    async with async_session_maker() as session:
        player = await QuestService.get_player_by_steam_id(session, data.get('Player').get('steamID'))
        response_data = {
            "steam_id": player.steam_id,
            "msg": ""
        }
        quest_activity_player = await update_activity_player(session, player, data.get('Player').get('activity'), response_data)
        if quest_activity_player["msg"]:
            response_data = quest_activity_player

        arena_match = await update_arena_match(data, session, player)
