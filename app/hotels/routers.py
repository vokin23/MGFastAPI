from fastapi import APIRouter, Query
from app.datebase import async_session_maker
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


@hotels_router.get("/{hotel_id}", summary="Получение отеля по id")
async def get_hotel(hotel_id: int):
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(id=hotel_id)


@hotels_router.post("/", summary="Создание отеля")
async def create_hotel(hotel_data: HotelsPost):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status": "OK", "data": hotel}


@hotels_router.put("/{hotel_id}", summary="Редактирование отеля")
async def edit_hotel(hotel_id: int, hotel_data: HotelsPut):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {"status": "OK"}


@hotels_router.delete("/{hotel_id}", summary="Удаление отеля")
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete_obj(id=hotel_id)
        await session.commit()
    return {"status": "OK"}


@hotels_router.patch("/{hotel_id}", summary="Частичное редактирование отеля")
async def patch_hotel(hotel_id: int, hotel_data: HotelsPatch):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id, exclude_unset=True)
        await session.commit()
    return {"status": "OK"}
