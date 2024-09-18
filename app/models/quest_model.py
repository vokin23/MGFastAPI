import enum
from sqlalchemy import String, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.datebase import Base
from app.models.player_model import Player


class AwardAPI(Base):
    __tablename__ = 'award_api'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    method: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255))
    count: Mapped[int] = mapped_column()


class ReputationType(Base):
    __tablename__ = 'reputation_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    static: Mapped[bool] = mapped_column(default=False)


class Operator(Base):
    __tablename__ = 'operator'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255), default="")
    class_name: Mapped[str] = mapped_column(String(255), default="")
    reputation_type_id: Mapped[int] = mapped_column(ForeignKey('reputation_type.id'))
    position: Mapped[str] = mapped_column(String(100))
    orientation: Mapped[str] = mapped_column(String(100))
    clothes: Mapped[JSON] = mapped_column(JSON)
    reputation_type = relationship('ReputationType', backref='operator_refs', overlaps="operators,reputation_type_backref")


class QuestType(enum.Enum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    lore = 'lore'


class Quest(Base):
    __tablename__ = 'quest'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default='quests')
    type: Mapped[QuestType] = mapped_column(Enum(QuestType))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    awards: Mapped[JSON] = mapped_column(JSON, nullable=True)
    awards_api: Mapped[int] = mapped_column(ForeignKey(AwardAPI.id), nullable=True, default=None)
    conditions: Mapped[JSON] = mapped_column(JSON, default=dict)
    required_items: Mapped[JSON] = mapped_column(JSON, nullable=True)
    operator_id: Mapped[int] = mapped_column(ForeignKey(Operator.id))
    reputation_need: Mapped[int] = mapped_column(default=0)
    reputation_add: Mapped[int] = mapped_column(default=0)
    reputation_minus: Mapped[int] = mapped_column(default=0)
    operator = relationship('Operator', backref='quests')


class Activity(Base):
    __tablename__ = 'activity'
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey(Player.id))
    quest_id: Mapped[int] = mapped_column(ForeignKey(Quest.id))
    conditions: Mapped[JSON] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_completed: Mapped[bool] = mapped_column(default=False)
    award_take: Mapped[bool] = mapped_column(default=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime)
    player = relationship('Player', backref="player_activities")
    quest = relationship('Quest', backref='activities')


class Action(Base):
    __tablename__ = 'action'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    request_json: Mapped[JSON] = mapped_column(JSON, default=dict)


class GameNameAnimal(Base):
    __tablename__ = 'game_name_animal'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    class_name: Mapped[str] = mapped_column(String(255))


class BoostReputationVip(Base):
    __tablename__ = 'boost_reputation_vip'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255), default="Прибавляет к репутации поле boost_value")
    level: Mapped[int] = mapped_column()
    boost_value: Mapped[int] = mapped_column(default=0)
