from app.models.users_models import UserModel
from app.repositories.base_repository import BaseRepository
from app.schemas.users_schemas import User


class UsersRepository(BaseRepository):
    model = UserModel
    schema = User
