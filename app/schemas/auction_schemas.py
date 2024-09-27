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
    category: int
    player: int
    steam_id: str
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


class MsgSchema(BaseModel):
    steam_id: str | None
    msg: str | None


class ProductsAndMsgSchema(BaseModel):
    steam_id: str | None
    msg: str | None
    products: List[ProductBaseSchema]


class BetBaseSchema(BaseModel):
    id: int
    product: int
    player: int
    price: int
    returned: bool
    time_created: datetime


class BetCreateSchema(BaseModel):
    product: int
    steam_id: str
    price: int
