from datetime import datetime, timedelta
import aiofiles
import json

from fastapi import HTTPException
from sqlalchemy import select, insert

from app.models.auction_model import Product, Bet
from app.models.player_model import Player
from app.schemas.auction_schemas import MsgSchema
from app.service.base_service import get_moscow_time


class AuctionService:
    @staticmethod
    async def rewards(steam_id, product):
        dir_rewards = '/config/profiles'
        awards_file_dir = f'{dir_rewards}/{steam_id}.json'
        try:
            async with aiofiles.open(awards_file_dir, 'r', encoding='utf-8') as f:
                awards = json.loads(await f.read())
            awards['awards'].append(product.attachment)
            async with aiofiles.open(awards_file_dir, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(awards, ensure_ascii=False, indent=4))
        except:
            awards = {
                "awards": []
            }
            awards['awards'].append(product.attachment)
            async with aiofiles.open(awards_file_dir, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(awards, ensure_ascii=False, indent=4))
    @staticmethod
    def calculate_remaining_time(time_created, duration):
        """
        Вычисляет оставшееся время аукциона.
        """
        end_time = time_created + timedelta(days=duration)
        remaining_time = end_time - get_moscow_time()

        # Преобразуем remaining_time в удобочитаемый формат
        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{days} дней {hours} часов {minutes} минут {seconds} секунд"

    @staticmethod
    def calculate_remaining_time_int(time_created, duration):
        """
        Вычисляет оставшееся время аукциона.
        """
        end_time = time_created + timedelta(days=duration)
        remaining_time = end_time - get_moscow_time()

        # Преобразуем remaining_time в удобочитаемый формат
        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return seconds + minutes*60 + hours*3600 + days*24*3600

    @staticmethod
    async def get_player(session, steam_id):
        player_obj = await session.execute(select(Player).where(Player.steam_id == steam_id))
        player = player_obj.scalar()
        if not player:
            raise HTTPException(status_code=404, detail="Игрок не найден")
        return player

    @staticmethod
    async def get_product(session, product_id):
        product_obj = await session.execute(select(Product).where(Product.id == product_id))
        product = product_obj.scalar()
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        return product

    @staticmethod
    async def get_owner(session, player_id):
        owner_obj = await session.execute(select(Player).where(Player.id == player_id))
        return owner_obj.scalar()

    @staticmethod
    async def get_last_bet(session, product_id):
        last_bet_obj = select(Bet).where(Bet.product == product_id, Bet.returned == False)
        last_bet = await session.execute(last_bet_obj)
        return last_bet.scalar()

    @staticmethod
    async def check_bet_conditions(player, product, bet_price, last_bet):
        if player.id == last_bet.player:
            return MsgSchema(steam_id=player.steam_id, msg="Вы уже сделали ставку на данный продукт!")
        if player.game_balance < bet_price:
            return MsgSchema(steam_id=player.steam_id, msg="Недостаточно средств для ставки!")
        if product.price + product.price_step > bet_price:
            return MsgSchema(steam_id=player.steam_id, msg="Ваша ставка должна быть выше минимальной ставки!")
        if last_bet and last_bet.player == player.id:
            return MsgSchema(steam_id=player.steam_id, msg="Вы уже сделали ставку на данный продукт!")
        return None

    @staticmethod
    async def handle_winning_bet(session, player, product, bet_price, last_bet, owner):
        player.game_balance -= product.price_sell
        await AuctionService.rewards(player.steam_id, product)
        product.status = False
        product.price = product.price_sell
        response_for_player = MsgSchema(steam_id=player.steam_id,
                                        msg=f"Поздравляем! Вы выиграли аукцион! Ваш приз: {product.name}")
        response_for_owner = MsgSchema(steam_id=owner.steam_id, msg=f"Аукцион завершен! Ваш {product.name} был продан")
        if last_bet:
            old_better_obj = await session.execute(select(Player).where(Player.id == last_bet.player))
            old_better = old_better_obj.scalar()
            old_better.game_balance += last_bet.price
            last_bet.returned = True
        new_bet = insert(Bet).values(product=product.id, player=player.id, price=bet_price)
        await session.execute(new_bet)
        return response_for_player, response_for_owner

    @staticmethod
    async def handle_regular_bet(session, player, product, bet_price, last_bet, owner):
        player.game_balance -= bet_price
        product.price = bet_price
        response_for_player = MsgSchema(steam_id=player.steam_id,
                                        msg=f"Ваша ставка принята! Ставка на данный момент: {bet_price}")
        response_for_owner = MsgSchema(steam_id=owner.steam_id,
                                       msg=f"На ваш продукт сделали ставку в размере: {bet_price}")
        if last_bet:
            old_better_obj = await session.execute(select(Player).where(Player.id == last_bet.player))
            old_better = old_better_obj.scalar()
            old_better.game_balance += last_bet.price
            last_bet.returned = True
        new_bet = insert(Bet).values(product=product.id, player=player.id, price=bet_price)
        await session.execute(new_bet)
        return response_for_player, response_for_owner