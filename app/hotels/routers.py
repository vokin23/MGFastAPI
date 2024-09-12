from fastapi import APIRouter, Query, Body
from sqlalchemy import insert, select
import asyncio
from app.datebase import async_session_maker
from app.hotels.models import HotelsModel
from app.hotels.schemas import HotelsPatch, HotelsPut, HotelsPost
from app.pagination import PaginationDep

hotels_router = APIRouter(prefix="/hotels")


@hotels_router.get("/", summary="Получение списка отелей")
async def get_hotels(
        pagination: PaginationDep,
        location: str | None = Query(None, description="Локация отеля"),
        title: str | None = Query(None, description="Название отеля")
):
    per_page = pagination.per_page or 4
    async with async_session_maker() as session:
        query = select(HotelsModel)
        if location:
            location = location.lower()
            query = query.filter(HotelsModel.location.ilike(f"%{location}%"))
        if title:
            title = title.lower()
            query = query.filter(HotelsModel.title.ilike(f"%{title}%"))
        query = (
            query
            .limit(per_page)
            .offset((pagination.page - 1) * per_page)
        )
        result = await session.execute(query)
        hotels = result.scalar().all()
        return hotels


@hotels_router.post("/", summary="Создание отеля")
async def create_hotel(hotel_data: HotelsPost):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(HotelsModel).values(**hotel_data.model_dump())
        await session.execute(add_hotel_stmt)
        await session.commit()
    return {"status": "OK"}


@hotels_router.delete("/{hotel_id}", summary="Удаление отеля")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}


@hotels_router.put("/{hotel_id}", summary="Обновление отеля")
def put_hotel(hotel_id: int, hotel_dta: HotelsPut):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_dta.title
            hotel["name"] = hotel_dta.name
            break
    return {"status": "OK"}


@hotels_router.patch("/{hotel_id}", summary="Частичное обновление отеля")
def patch_hotel(hotel_id: int, hotel_data: HotelsPatch):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if hotel_data.title:
                hotel["title"] = hotel_data.title
            if hotel_data.name:
                hotel["name"] = hotel_data.name
            break
    return {"status": "OK"}
