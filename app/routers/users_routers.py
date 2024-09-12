from fastapi import APIRouter

from passlib.context import CryptContext

from app.models.datebase import async_session_maker
from app.repositories.users_repository import UsersRepository
from app.schemas.users_schemas import UsersCreate, UsersAdd

users_router = APIRouter(prefix="/users")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@users_router.post("/register", summary="Создание пользователя")
async def register_user(data: UsersAdd):
    hashed_password = pwd_context.hash(data.password)
    new_user_data = UsersCreate(email=data.email, hashed_password=hashed_password, first_name=data.first_name, last_name=data.last_name)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()
    return {"status": "OK"}
