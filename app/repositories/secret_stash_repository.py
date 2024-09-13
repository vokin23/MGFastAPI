import random

from app.models.secret_stash_models import Stash, StashCategory
from app.schemas.secret_stash_schemas import SecretStashSchema, SecretStashOpenSchema, SecretStashCategorySchema
from app.repositories.base_repository import BaseRepository


class StashRepository(BaseRepository):
    model = Stash
    schema = SecretStashSchema

    async def open_stash(self, stash_id: int, steam_id: str) -> SecretStashOpenSchema:
        stash = await self.get_one_or_none(id=stash_id)
        if stash:
            if stash.is_opened:
                return SecretStashOpenSchema(steam_id=steam_id, msg="Похоже, что схрон уже открыли до вас",
                                             awards=[None])
            stash_category = stash.category
            awards_list = stash_category.awards_list
            awards = random.choice(awards_list)
            award_response = []
            for award in awards.keys():
                award_response.append({
                    "class_name": award,
                    "value": awards[award]
                })
            stash.is_opened = True
            await self.session.commit()
            return SecretStashOpenSchema(steam_id=steam_id, msg="Поздравляем! Вы открыли схрон и получили награду",
                                         awards=award_response)


class StashCategoryRepository(BaseRepository):
    model = StashCategory
    schema = SecretStashCategorySchema
