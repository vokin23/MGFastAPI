from sqlalchemy import select, func, insert

from app.models.hotels_models import HotelsModel, RoomsModel
from app.schemas.hotels_schemas import Hotel
from app.repositories.base_repository import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsModel
    schema = Hotel

    async def get_all(self, location, title, limit, offset):
        query = select(HotelsModel)
        if location:
            location = location.lower()
            query = query.filter(func.lower(HotelsModel.location).ilike(f"%{location}%"))
        if title:
            title = title.lower()
            query = query.filter(func.lower(HotelsModel.title).ilike(f"%{title}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().all()]

    async def add(self, hotel_data):
        add_hotel_stmt = insert(self.model).values(**hotel_data.dict()).returning(self.model)
        result = await self.session.execute(add_hotel_stmt)
        return result.scalars().one_or_none()


class RoomsRepository(BaseRepository):
    model = RoomsModel
