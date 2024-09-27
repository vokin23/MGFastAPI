from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.datebase import Base


class Stash(Base):
    __tablename__ = 'stash'

    id: Mapped[int] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column(String(length=255))
    position: Mapped[str] = mapped_column(String(length=255))
    orientation: Mapped[str] = mapped_column(String(length=255))
    category_id: Mapped[int] = mapped_column(ForeignKey('stash_category.id'))
    is_opened: Mapped[bool] = mapped_column(default=False)


class StashCategory(Base):
    __tablename__ = 'stash_category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=255))
    description: Mapped[str] = mapped_column(String(length=255))
    awards_list: Mapped[JSON] = mapped_column(JSON)
    filling: Mapped[int] = mapped_column(default=100, nullable=True)
