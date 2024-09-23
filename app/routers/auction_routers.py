import random
from datetime import datetime
from typing import List

import pytz
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.auction_model import Product, Category
from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.auction_schemas import ProductCreateSchema, ProductBaseSchema, CategoryCreateSchema, CategoryBaseSchema
from app.service.auction_service import AuctionService
from app.service.base_service import get_moscow_time

auction_router = APIRouter(prefix="/auction")
admin_router = APIRouter()



@admin_router.post("/create_auction_category", summary="Создание категории продукта")
async def create_auction_category(data: CategoryCreateSchema) -> CategoryBaseSchema:
    async with async_session_maker() as session:
        new_category = insert(Category).values(
            name=data.name
        )
        category = await session.execute(new_category)
        await session.commit()
        return category.scalar()



@auction_router.post("/create_product", summary="Создание продукта")
async def create_product(data: ProductCreateSchema) -> ProductBaseSchema:
    async with async_session_maker() as session:
        player_obj = await session.execute(select(Player).where(Player.steam_id == data.steam_id))
        player = player_obj.scalar()
        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        new_product = insert(Product).values(
            flag=False,
            status=True,
            name=data.name,
            class_name=data.class_name,
            description=data.description,
            category=data.category,
            player=player.id,
            quantity=data.quantity,
            time_created=get_moscow_time(),
            duration=3,
            remaining_time=AuctionService.calculate_remaining_time,
            remaining_time_int=AuctionService.calculate_remaining_time_int,
            is_attachment=data.is_attachment,
            attachment=data.attachment,
            price=data.price,
            price_step=data.price_step,
            price_sell=data.price_sell
        )
        product = await session.execute(new_product)
        await session.commit()
        return product.scalar()