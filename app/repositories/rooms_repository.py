from app.hotels.models import RoomsModel
from app.repositories.base_repository import BaseRepository


class HotelsRepository(BaseRepository):
    model = RoomsModel
