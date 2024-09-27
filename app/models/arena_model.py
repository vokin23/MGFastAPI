from sqlalchemy import String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.datebase import Base


class Arena(Base):
    __tablename__ = 'arena'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    cords_spawn: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    cloths: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    free: Mapped[bool] = mapped_column(default=True)


class Match(Base):
    __tablename__ = 'match'

    id: Mapped[int] = mapped_column(primary_key=True)
    arena: Mapped[int] = mapped_column(ForeignKey('arena.id'))
    player1: Mapped[int] = mapped_column(ForeignKey('player.id'), nullable=True, default=None)
    old_things_player1: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    old_cords_player1: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    player2: Mapped[int] = mapped_column(ForeignKey('player.id'), nullable=True, default=None)
    old_things_player2: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    old_cords_player2: Mapped[JSON] = mapped_column(JSON, nullable=True, default=None)
    time_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    time_start: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    time_end: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    start: Mapped[bool] = mapped_column(default=False)
    finished: Mapped[bool] = mapped_column(default=False)
    winner: Mapped[int] = mapped_column(ForeignKey('player.id'), nullable=True, default=None)
