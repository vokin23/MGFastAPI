from sqlalchemy import String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.datebase import Base


class Player(Base):
    __tablename__ = 'player'

    id: Mapped[int] = mapped_column(primary_key=True)
    steam_id: Mapped[str] = mapped_column(String(17), unique=True)
    game_balance: Mapped[int] = mapped_column(default=0)
    site_balance: Mapped[int] = mapped_column(default=0)
    vip: Mapped[bool] = mapped_column(default=False)
    vip_lvl: Mapped[int] = mapped_column(default=0)
    reputation: Mapped[JSON] = mapped_column(JSON, default=dict)
    created_at_player: Mapped[datetime] = mapped_column(DateTime)
    created_at_vip: Mapped[datetime] = mapped_column(DateTime)
    date_end_vip: Mapped[datetime] = mapped_column(DateTime)
