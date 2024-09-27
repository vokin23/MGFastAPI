from typing import List
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.auction_model import Product, Category, Bet
from app.models.datebase import async_session_maker
from app.models.player_model import Player
from app.schemas.auction_schemas import ProductCreateSchema, ProductBaseSchema, CategoryCreateSchema, \
    CategoryBaseSchema, ProductsAndMsgSchema, BetCreateSchema, MsgSchema, BetBaseSchema
from app.service.auction_service import AuctionService
from app.service.base_service import get_moscow_time

auction_router = APIRouter(prefix="/auction")
admin_router = APIRouter(prefix="/auction")


@admin_router.post("/create_auction_category", summary="Создание категории продукта")
async def create_auction_category(data: CategoryCreateSchema) -> CategoryBaseSchema:
    async with async_session_maker() as session:
        new_category = insert(Category).values(
            name=data.name
        ).returning(Category)
        category = await session.execute(new_category)
        await session.commit()
        return category.scalar()


@admin_router.get("/get_auction_categories", summary="Получение категорий продуктов")
async def get_auction_categories() -> List[CategoryBaseSchema]:
    async with async_session_maker() as session:
        categories_obj = await session.execute(select(Category))
        categories = categories_obj.scalars().all()
        return categories


@auction_router.post("/create_product", summary="Создание продукта")
async def create_product(data: ProductCreateSchema) -> ProductBaseSchema:
    async with async_session_maker() as session:
        player_obj = await session.execute(select(Player).where(Player.steam_id == data.steam_id))
        player = player_obj.scalar()
        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        time_created = get_moscow_time()
        remaining_time = AuctionService.calculate_remaining_time(time_created=time_created, duration=3)
        remaining_time_int = AuctionService.calculate_remaining_time_int(time_created=time_created, duration=3)
        new_product = insert(Product).values(
            flag=False,
            status=True,
            name=data.name,
            class_name=data.class_name,
            description=data.description,
            category=data.category,
            player=player.id,
            steam_id=data.steam_id,
            quantity=data.quantity,
            time_created=time_created,
            duration=3,
            remaining_time=remaining_time,
            remaining_time_int=remaining_time_int,
            is_attachment=data.is_attachment,
            attachment=data.attachment,
            price=data.price,
            price_step=data.price_step,
            price_sell=data.price_sell
        ).returning(Product)
        product = await session.execute(new_product)
        await session.commit()
        return product.scalar()


@auction_router.get("/get_products", summary="Получение продуктов по категории")
async def get_products(category_id: int = Query(description="ID категории")) -> ProductsAndMsgSchema:
    async with async_session_maker() as session:
        response_data = {
            "steam_id": None,
            "msg": None,
            "products": []
        }
        products_obj = await session.execute(
            select(Product).where(Product.category == category_id, Product.status == True))
        products = products_obj.scalars().all()
        response_data["products"] = products
        for product in products:
            product.remaining_time = AuctionService.calculate_remaining_time(time_created=product.time_created,
                                                                             duration=product.duration)
            product.remaining_time_int = AuctionService.calculate_remaining_time_int(time_created=product.time_created,
                                                                                     duration=product.duration)
            if product.remaining_time_int <= 0:
                product.status = False
                last_bet_obj = select(Bet).where(Bet.product == product.id, Bet.returned == False)
                last_bet = await session.execute(last_bet_obj)
                last_bet = last_bet.scalar()
                if last_bet:
                    player_obj = await session.execute(select(Player).where(Player.id == last_bet.player))
                    player = player_obj.scalar()
                    await AuctionService.rewards(player.steam_id, product)
                    owner_obj = await session.execute(select(Player).where(Player.id == product.player))
                    owner = owner_obj.scalar()
                    owner.game_balance += last_bet.price
                    response_data = {
                        "steam_id": player.steam_id,
                        "msg": f"Поздравляем! Вы выиграли аукцион! Ваш приз: {product.name}"
                    }
                else:
                    player_obj = await session.execute(select(Player).where(Player.id == product.player))
                    player = player_obj.scalar()
                    await AuctionService.rewards(player.steam_id, product)
                    response_data = {
                        "steam_id": player.steam_id,
                        "msg": f"Аукцион завершен! Ваш {product.name} не был продан"
                    }
        await session.commit()
        return ProductsAndMsgSchema(**response_data)


@auction_router.post("/create_bet", summary="Создание ставки")
async def create_bet(data: BetCreateSchema) -> List[MsgSchema]:
    async with async_session_maker() as session:
        player = await AuctionService.get_player(session, data.steam_id)
        product = await AuctionService.get_product(session, data.product)
        product.flag = True
        await session.commit()
        owner = await AuctionService.get_owner(session, product.player)

        if owner.steam_id == player.steam_id:
            return [MsgSchema(steam_id=player.steam_id, msg="Вы не можете делать ставки на свой же продукт!")]

        last_bet = await AuctionService.get_last_bet(session, product.id)
        bet_price = data.price

        error_msg = await AuctionService.check_bet_conditions(player, product, bet_price, last_bet)
        if error_msg:
            return [error_msg]

        if product.price_sell <= bet_price:
            response_for_player, response_for_owner = await AuctionService.handle_winning_bet(session, player, product, bet_price, last_bet, owner)
        else:
            response_for_player, response_for_owner = await AuctionService.handle_regular_bet(session, player, product, bet_price, last_bet, owner)

        product.flag = False
        await session.commit()
        return [response_for_player, response_for_owner]


@admin_router.get("/get_auction_products", summary="Получение продуктов")
async def get_auction_products() -> List[ProductBaseSchema]:
    async with async_session_maker() as session:
        products_obj = await session.execute(select(Product).where(Product.status == True))
        products = products_obj.scalars().all()
        for product in products:
            product.remaining_time = AuctionService.calculate_remaining_time(time_created=product.time_created,
                                                                             duration=product.duration)
            product.remaining_time_int = AuctionService.calculate_remaining_time_int(time_created=product.time_created,
                                                                                     duration=product.duration)
            if product.remaining_time_int <= 0:
                product.status = False
                last_bet_obj = select(Bet).where(Bet.product == product.id, Bet.returned == False)
                last_bet = await session.execute(last_bet_obj)
                last_bet = last_bet.scalar()
                if last_bet:
                    player_obj = await session.execute(select(Player).where(Player.id == last_bet.player))
                    player = player_obj.scalar()
                    await AuctionService.rewards(player.steam_id, product)
                    owner_obj = await session.execute(select(Player).where(Player.id == product.player))
                    owner = owner_obj.scalar()
                    owner.game_balance += last_bet.price
                else:
                    player_obj = await session.execute(select(Player).where(Player.id == product.player))
                    player = player_obj.scalar()
                    await AuctionService.rewards(player.steam_id, product)
        await session.commit()
        return products


@admin_router.get("/get_auction_bets", summary="Получение ставок")
async def get_auction_bets() -> List[BetBaseSchema]:
    async with async_session_maker() as session:
        bets_obj = await session.execute(select(Bet))
        bets = bets_obj.scalars().all()
        return bets


@admin_router.get("/get_actual_bets", summary="Получение актуальных ставок")
async def get_actual_bets() -> List[BetBaseSchema]:
    async with async_session_maker() as session:
        bets_obj = await session.execute(select(Bet).where(Bet.returned == False))
        bets = bets_obj.scalars().all()
        return bets
