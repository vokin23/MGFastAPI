from datetime import datetime, timedelta
from typing import List

import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from app.models.player_model import Player
from app.models.quest_model import Quest, Operator, Activity, ReputationType, GameNameAnimal, Action, BoostReputationVip
from app.schemas.quest_schemas import ActivityCreate


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
    async def get_quests_by_operator(session: AsyncSession, operator: Operator) -> List[Quest]:
        result = await session.execute(select(Quest).where(Quest.operator == operator.id))
        return result.scalars().all()

    @staticmethod
    async def get_activity_by_player(session: AsyncSession, player: Player) -> List[Activity]:
        result = await session.execute(select(Activity).where(Activity.player == player.id))
        return result.scalars().all()

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
    async def get_operator_by_id(session: AsyncSession, operator_id: int) -> Operator:
        result = await session.execute(select(Operator).where(Operator.id == operator_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_reputation(session: AsyncSession, player: Player, quest: Quest, activity: Activity):
        operator = await QuestService.get_operator_by_quest(session, quest)
        operator_reputation_type = await QuestService.get_reputation_type_by_id(session, operator.reputation_type)
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

    @staticmethod
    async def update_game_activity_player(session: AsyncSession, activitys: List[Activity], activity_type: dict) -> ActivityCreate:
        async def help_func(activity_game, param=1):
            data_response = {
                "steam_id": None,
                "msg": None
            }
            for activity in activitys:
                activity_quest = await QuestService.get_quest_by_id(session, activity.quest)
                if not activity_quest.required_items and activity_game in activity.conditions.keys():
                    if activity.conditions['need'] - param > activity.conditions['progress']:
                        activity.conditions['progress'] += param
                    else:
                        activity.conditions['progress'] = activity.conditions['need']
                        activity.is_completed = True
                        player = await QuestService.get_player_by_steam_id(session, activity.player)
                        data_response = {
                            "steam_id": player.steam_id,
                            "msg": 'Вы выполнили квест!'
                        }
            return data_response

        match activity_type:
            case 'MG_Activity_AnimalKillHandler':
                activity_game = activity_type['AnimalData']['typeName']
                data_response = await help_func(activity_game)
                return ActivityCreate(**data_response)
            case 'MG_Activity_ZombieKillHandler':
                activity_game = activity_type['ZombieData']['typeName']
                data_response = await help_func(activity_game)
                return ActivityCreate(**data_response)
            case 'ActionOpenStashCase':
                activity_game = activity_type['ActionOpenStashCase']
                data_response = await help_func(activity_game)
                return ActivityCreate(**data_response)
            case 'ActionSkinning':
                activity_game = activity_type['ActionOpenStashCase']
                data_response = await help_func(activity_game)
                return ActivityCreate(**data_response)
            case 'DistanceActivity':
                param = int(activity_type['distance'])
                data_response = await help_func('DistanceActivity', param)
                return ActivityCreate(**data_response)


    @classmethod
    async def check_player_activity(cls, session: AsyncSession, player: Player, quest) -> ActivityCreate:
        moscow_tz = cls.moscow_tz
        player_activity = await session.execute(select(Activity).where(Activity.player == player.id))
        player_activity = player_activity.scalars().all()
        reputation_type = await cls.get_reputation_type_by_id(session, quest.operator)

        daily_activity = [act for act in player_activity if act.quest.type == 'daily']
        weekly_activity = [act for act in player_activity if act.quest.type == 'weekly']
        monthly_activity = [act for act in player_activity if act.quest.type == 'monthly']

        sorted_daily_activity = sorted(daily_activity, key=lambda act: act.active_changed_at.astimezone(moscow_tz),
                                       reverse=True)
        sorted_weekly_activity = sorted(weekly_activity, key=lambda act: act.active_changed_at.astimezone(moscow_tz),
                                        reverse=True)
        sorted_monthly_activity = sorted(monthly_activity, key=lambda act: act.active_changed_at.astimezone(moscow_tz),
                                         reverse=True)

        last_daily_activity = sorted_daily_activity[0] if sorted_daily_activity else None
        last_weekly_activity = sorted_weekly_activity[0] if sorted_weekly_activity else None
        last_monthly_activity = sorted_monthly_activity[0] if sorted_monthly_activity else None

        moscow_now = datetime.now(cls.moscow_tz)

        if last_daily_activity and quest.type == 'daily':
            if not (moscow_now.date() >= (
                    last_daily_activity.active_changed_at.astimezone(moscow_tz).date() + timedelta(days=1))):
                return ActivityCreate(**{
                    "steam_id": player.steam_id,
                    "msg": f'Вы можете начать выполнение ежедневного квеста только через 24 часа после завершения предыдущего!\n'
                           f'Попробуйте принять квест {last_daily_activity.active_changed_at.astimezone(moscow_tz).date() + timedelta(days=1)}'
                })
        elif last_weekly_activity and quest.type == 'weekly':
            if not (moscow_now.date() >= (
                    last_weekly_activity.active_changed_at.astimezone(moscow_tz).date() + timedelta(days=7))):
                return ActivityCreate(**{
                    "steam_id": player.steam_id,
                    "msg": f'Вы можете начать выполнение еженедельного квеста только через 7 дней после завершения предыдущего!\n'
                           f'Попробуйте принять квест {last_weekly_activity.active_changed_at.astimezone(moscow_tz).date() + timedelta(days=7)}'
                })
        elif last_monthly_activity and quest.type == 'monthly':
            if not (moscow_now.date() >= (
                    last_monthly_activity.active_changed_at.astimezone(moscow_tz).date() + timedelta(days=30))):
                return ActivityCreate(**{
                    "steam_id": player.steam_id,
                    "msg": f'Вы можете начать выполнение ежемесячного квеста только через 30 дней после завершения предыдущего!\n'
                           f'Попробуйте принять квест {last_monthly_activity.active_changed_at.astimezone(moscow_tz).date() + timedelta(days=30)}'
                })
        elif len([act for act in player_activity if act.is_active]) == 4:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'У вас уже есть 4 активных квеста!'
            })
        elif quest in [act.quest for act in player_activity]:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'Вы уже выполняете этот квест'
            })
        elif quest.reputation_need > player.reputation[reputation_type.name]:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'У вас недостаточно репутации для выполнения этого квеста'
            })
        elif quest.type == 'daily' and len(
                [act.quest for act in player_activity if act.quest.type == 'daily' and act.is_active]) == 1:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'Вы уже выполняете ежедневный квест'
            })
        elif quest.type == 'weekly' and len(
                [act.quest for act in player_activity if act.quest.type == 'weekly' and act.is_active]) == 1:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'Вы уже выполняете еженедельный квест'
            })
        elif quest.type == 'monthly' and len(
                [act.quest for act in player_activity if act.quest.type == 'monthly' and act.is_active]) == 1:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'Вы уже выполняете ежемесячный квест'
            })
        elif quest.type == 'lore' and len(
                [act.quest for act in player_activity if act.quest.type == 'lore' and act.is_active]) == 1:
            return ActivityCreate(**{
                "steam_id": player.steam_id,
                "msg": 'Вы уже выполняете лорный квест'
            })
