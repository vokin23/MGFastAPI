from sqlalchemy import String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.datebase import Base


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    flag: Mapped[bool] = mapped_column(default=False)
    status: Mapped[bool] = mapped_column(default=True)
    name: Mapped[str] = mapped_column(String(100))
    class_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    category: Mapped[int] = mapped_column(ForeignKey('category.id'))
    player: Mapped[int] = mapped_column(ForeignKey('player.id'))
    quantity: Mapped[int] = mapped_column()
    time_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    duration: Mapped[int] = mapped_column(default=3)
    remaining_time: Mapped[str] = mapped_column(String(40), default='')
    remaining_time_int: Mapped[int] = mapped_column(default=0)
    is_attachment: Mapped[bool] = mapped_column(default=False)
    attachment: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    price: Mapped[int] = mapped_column()
    price_step: Mapped[int] = mapped_column()
    price_sell: Mapped[int] = mapped_column()


class Bet(Base):
    __tablename__ = 'bet'

    id: Mapped[int] = mapped_column(primary_key=True)
    product: Mapped[int] = mapped_column(ForeignKey('product.id'))
    player: Mapped[int] = mapped_column(ForeignKey('player.id'))
    price: Mapped[int] = mapped_column()
    returned: Mapped[bool] = mapped_column(default=False)
    time_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

