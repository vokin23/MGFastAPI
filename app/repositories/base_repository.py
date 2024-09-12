from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def edit(self, data: BaseModel, **filter_by) -> None:
        stmt = (
            update(self.model)
            .where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
            .values(**data.model_dump())
        )
        await self.session.execute(stmt)

    async def delete_obj(self, **filter_by) -> None:
        stmt = (
            delete(self.model)
            .where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
        )
        await self.session.execute(stmt)
