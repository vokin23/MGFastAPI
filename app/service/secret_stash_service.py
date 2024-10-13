import random

from sqlalchemy import select

from app.models.secret_stash_models import StashCategory
from app.schemas.secret_stash_schemas import SecretStashSchema, SecretStashOpenSchema
from app.service.base_service import read_json_async


class SecretStashService:
    @staticmethod
    async def open_stash(session, stash, player) -> SecretStashOpenSchema:
        stmt_category = await session.execute(select(StashCategory).where(StashCategory.id == stash.category_id))
        category = stmt_category.scalar_one()
        awards_list = category.awards_list

        random_awards = []
        block_awards = []

        if player.exp:
            for exp in player.exp:
                if exp['EXP_ID'] == 0:
                    exp_lvl = exp['Lvl']
                    break
        else:
            try:
                directory_path = '/app/PlayersDB'
                player_json = await read_json_async(f'{directory_path}/{player.steam_id}.json')
                exp_json = player_json['EXP']
                if exp_json:
                    player.exp = exp_json
                    await session.commit()
                    for exp in exp_json:
                        if exp['EXP_ID'] == 0:
                            exp_lvl = exp['Lvl']
                            break
            except FileNotFoundError:
                exp_lvl = 0

        if exp_lvl <= 14:
            count_type_awards = 1
        elif 15 <= exp_lvl <= 24:
            count_type_awards = 2 if player.vip_lvl > 1 else 1
        elif 25 <= exp_lvl <= 34:
            if player.vip_lvl == 4:
                count_type_awards = 3
            elif player.vip_lvl > 1:
                count_type_awards = 2
            else:
                count_type_awards = 1
        elif 35 <= exp_lvl <= 49:
            if player.vip_lvl == 4:
                count_type_awards = 4
            elif player.vip_lvl > 1:
                count_type_awards = 3
            else:
                count_type_awards = 2
        elif exp_lvl == 50:
            if player.vip_lvl == 4:
                count_type_awards = 5
            elif player.vip_lvl > 1:
                count_type_awards = 4
            else:
                count_type_awards = 3

        if len(awards_list) > count_type_awards:
            while len(random_awards) < count_type_awards:
                awards = random.choice(awards_list)
                if awards in block_awards:
                    continue
                block_awards.append(awards)
                count_awards = round(len(awards) * category.filling / 100)
                random_awards.extend(random.sample(awards, count_awards))
        else:
            for awards in awards_list:
                count_awards = round(len(awards) * category.filling / 100)
                random_awards.extend(random.sample(awards, count_awards))
            for _ in range(count_type_awards - len(awards_list)):
                awards = random.choice(awards_list)
                count_awards = round(len(awards) * category.filling / 100)
                random_awards.extend(random.sample(awards, count_awards))
        response_data = {
            "steam_id": player.steam_id,
            "stash_id": stash.id,
            "msg": "Поздравляем! Вы открыли схрон и получили награду",
            "awards": random_awards
        }
        stash.is_opened = True
        await session.commit()
        return SecretStashOpenSchema(**response_data)
