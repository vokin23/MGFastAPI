from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        return self.schema.model_validate(model) if model else None

    async def add(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        return self.schema.model_validate(model)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        stmt = update(self.model).filter_by(**filter_by).values(**data.model_dump(exclude_unset=exclude_unset))
        await self.session.execute(stmt)

    async def delete_obj(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
