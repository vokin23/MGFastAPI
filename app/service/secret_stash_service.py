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
        print(awards)

        count_awards = round(len(awards) * category.filling / 100)
        random_awards = random.sample(awards, count_awards)
        print(random_awards)
        response_data = {
            "steam_id": steam_id,
            "msg": "Поздравляем! Вы открыли схрон и получили награду",
            "awards": random_awards
        }
        stash.is_opened = True
        await session.commit()
        return SecretStashOpenSchema(**response_data)
