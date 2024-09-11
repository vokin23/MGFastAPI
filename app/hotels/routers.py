from fastapi import APIRouter, Query, Body
from .schemas import HotelsPatch, HotelsPut, HotelsPost

hotels_router = APIRouter(prefix="/hotels")

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


@hotels_router.get("/", summary="Получение списка отелей")
def get_hotels(
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
        page: int | None = Query(1, description="Номер страницы", gt=1),
        limit: int | None = Query(3, description="Количество записей на странице", gt=1, le=100)
):
    global hotels
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    if page and limit:
        start = (page - 1) * limit
        end = start + limit
        hotels_ = hotels[start:end]
        return hotels_
    elif page:
        start = (page - 1) * 3
        end = start + 3
        hotels_ = hotels[start:end]
        return hotels_
    elif limit:
        hotels_ = hotels[:limit]
        return hotels_
    return hotels_


@hotels_router.post("/", summary="Создание отеля")
def create_hotel(hotel_data: HotelsPost):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": hotel_data.title,
        "name": hotel_data.name
    })
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