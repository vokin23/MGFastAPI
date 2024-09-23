from datetime import datetime, timedelta
from app.service.base_service import get_moscow_time


class AuctionService:
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