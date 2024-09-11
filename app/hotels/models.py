from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.datebase import Base


class HotelsModel(Base):
    __tablename__ = 'hotels'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=255))
    location: Mapped[str]
