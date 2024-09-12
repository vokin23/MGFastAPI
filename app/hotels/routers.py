from fastapi import APIRouter, Query, Body
from sqlalchemy import insert, select, func
import asyncio
from app.datebase import async_session_maker
from app.hotels.models import HotelsModel
from app.hotels.schemas import HotelsPatch, HotelsPut, HotelsPost
from app.pagination import PaginationDep
from app.repositories.hotels_repository import HotelsRepository

hotels_router = APIRouter(prefix="/hotels")


@hotels_router.get("/", summary="Получение списка отелей")
async def get_hotels(
        pagination: PaginationDep,
        location: str | None = Query(None, description="Локация отеля"),
        title: str | None = Query(None, description="Название отеля")
):
    limit = pagination.per_page or 5
    offset = (pagination.page - 1) * limit
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(location=location,
                                                       title=title,
                                                       limit=limit,
                                                       offset=offset)


@hotels_router.post("/", summary="Создание отеля")
async def create_hotel(hotel_data: HotelsPost):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add_hotel(hotel_data)
        await session.commit()
        return {"data": hotel._asdict() if hasattr(hotel, '_asdict') else dict(hotel)}
