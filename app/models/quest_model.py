from sqlalchemy import String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.datebase import Base
from app.models.player_model import Player


class ReputationType(Base):
    __tablename__ = 'reputation_type'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")


class Operator(Base):
    __tablename__ = 'operator'

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_name: Mapped[str] = mapped_column(String(255), default="")
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255), default="")
    class_name: Mapped[str] = mapped_column(String(255), default="")
    reputation_type: Mapped[str] = mapped_column(ForeignKey(ReputationType.id))
    position: Mapped[str] = mapped_column(String(100))
    orientation: Mapped[str] = mapped_column(String(100))
    clothes: Mapped[JSON] = mapped_column(JSON)


class Quest(Base):
    __tablename__ = 'quest'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default='quests')
    type: Mapped[str] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    awards: Mapped[JSON] = mapped_column(JSON)
    conditions: Mapped[JSON] = mapped_column(JSON, default=dict)
    required_items: Mapped[JSON] = mapped_column(JSON, default="")
    operator: Mapped[str] = mapped_column(ForeignKey(Operator.id))
    reputation_need: Mapped[int] = mapped_column(default=0)
    reputation_add: Mapped[int] = mapped_column(default=0)
    reputation_minus: Mapped[int] = mapped_column(default=0)


class Activity(Base):
    __tablename__ = 'activity'

    id: Mapped[int] = mapped_column(primary_key=True)
    player: Mapped[str] = mapped_column(ForeignKey(Player.id))
    quest: Mapped[str] = mapped_column(ForeignKey(Quest.id))
    conditions: Mapped[JSON] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_completed: Mapped[bool] = mapped_column(default=False)
    award_take: Mapped[bool] = mapped_column(default=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime)


class Action(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    request_json: Mapped[JSON] = mapped_column(JSON, default=dict)


class GameNameAnimal(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    class_name: Mapped[str] = mapped_column(String(255))
