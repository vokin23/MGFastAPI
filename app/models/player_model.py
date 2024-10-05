from sqlalchemy import String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.datebase import Base


class Player(Base):
    __tablename__ = 'player'

    id: Mapped[int] = mapped_column(primary_key=True)
    steam_id: Mapped[str] = mapped_column(String(17), unique=True)
    discord_name: Mapped[str] = mapped_column(String(50), default='')
    name: Mapped[str] = mapped_column(String(50), default='')
    surname: Mapped[str] = mapped_column(String(50), default='')
    avatar: Mapped[str] = mapped_column(String(255), default='')
    about: Mapped[str] = mapped_column(String(255), default='')
    survivor_model: Mapped[str] = mapped_column(String(255), default='')
    fraction_id: Mapped[int] = mapped_column(default=-1)
    prem_slot: Mapped[bool] = mapped_column(default=False)
    game_balance: Mapped[int] = mapped_column(default=0)
    site_balance: Mapped[int] = mapped_column(default=0)
    vip: Mapped[bool] = mapped_column(default=False)
    vip_lvl: Mapped[int] = mapped_column(default=0)
    reputation: Mapped[JSON] = mapped_column(JSON, default=list)
    exp: Mapped[JSON] = mapped_column(JSON, default=list)
    created_at_player: Mapped[datetime] = mapped_column(DateTime)
    created_at_vip: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    date_end_vip: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    arena_ranking: Mapped[int] = mapped_column(default=0)
    kills: Mapped[int] = mapped_column(default=0)
    deaths: Mapped[int] = mapped_column(default=0)


class Fraction(Base):
    __tablename__ = 'fraction'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    leader_steam_id: Mapped[str] = mapped_column(String(17))
    leader_name: Mapped[str] = mapped_column(String(50))
    logo: Mapped[str] = mapped_column(String(255))
    additional_ids: Mapped[JSON] = mapped_column(JSON, default=list)
    spawn_pos: Mapped[JSON] = mapped_column(JSON, default=list)
    max_staff: Mapped[int] = mapped_column(default=10)
