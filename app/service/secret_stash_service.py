import random

from sqlalchemy import select

from app.models.secret_stash_models import StashCategory
from app.schemas.secret_stash_schemas import SecretStashSchema, SecretStashOpenSchema


class SecretStashService:
    @staticmethod
    async def open_stash(session, stash, steam_id) -> SecretStashOpenSchema:
        stmt_category = await session.execute(select(StashCategory).where(StashCategory.id == stash.category_id))
        category = stmt_category.scalar_one()
        awards_list = category.awards_list
        awards = random.choice(awards_list)
        award_response = []

        count_awards = round(len(awards.keys()) * category.filling / 100)
        random_awards = random.sample(list(awards.keys()), count_awards)
        for award in random_awards:
            award_response.append({
                "class_name": award,
                "value": awards[award]
            })

        response_data = {
            "steam_id": steam_id,
            "msg": "Поздравляем! Вы открыли схрон и получили награду",
            "awards": award_response
        }
        stash.is_opened = True
        await session.commit()
        return SecretStashOpenSchema(**response_data)
