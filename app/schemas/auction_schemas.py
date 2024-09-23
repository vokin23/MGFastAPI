from typing import List
from datetime import datetime
from pydantic import BaseModel


class CategoryBaseSchema(BaseModel):
    id: int
    name: str

class CategoryCreateSchema(BaseModel):
    name: str


class ProductBaseSchema(BaseModel):
    id: int
    flag: bool
    status: bool
    name: str
    class_name: str
    description: str
    category: List[CategoryBaseSchema]
    player: str
    steam_id_user: str
    quantity: int
    time_created: datetime
    duration: int
    remaining_time: str
    remaining_time_int: int
    is_attachment: bool
    attachment: dict | None
    price: int
    price_step: int
    price_sell: int


class ProductCreateSchema(BaseModel):
    name: str
    class_name: str
    description: str
    category: int
    steam_id: str
    quantity: int
    is_attachment: bool
    attachment: dict | None
    price: int
    price_step: int
    price_sell: int