from fastapi import APIRouter, Query, Body
from .schemas import HotelsSchemas

hotels_router = APIRouter(prefix="/hotels")

hotels = [
    {"id": 1, "title": "Sochi", "name": "Radisson"},
    {"id": 2, "title": "Дубай", "name": "Burj Al Arab"},
]


@hotels_router.get("/", summary="Получение списка отелей")
def get_hotels(
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    return hotels_


@hotels_router.post("/", summary="Создание отеля")
def create_hotel(hotel_data: HotelsSchemas):
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
def put_hotel(hotel_id: int, hotel_dta: HotelsSchemas):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_dta.title
            hotel["name"] = hotel_dta.name
            break
    return {"status": "OK"}


@hotels_router.patch("/{hotel_id}", summary="Частичное обновление отеля")
def patch_hotel(hotel_id: int, title: str | None = Body(), name: str | None = Body()):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if title:
                hotel["title"] = title
            if name:
                hotel["name"] = name
            break
    return {"status": "OK"}