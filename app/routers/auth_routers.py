from fastapi import APIRouter, HTTPException, Response, Request
from starlette.requests import Request

from app.repositories.users_repository import UsersRepository
from app.models.datebase import async_session_maker
from app.schemas.users_schemas import UserRequestAdd, UserAdd
from app.service.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
        data: UserRequestAdd,
):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()

    return {"status": "OK"}


@router.post("/login")
async def login_user(
        data: UserRequestAdd,
        response: Response,
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Пароль неверный")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}


@router.get("/only_auth")
async def only_auth(
        request: Request,
):
    access_token = request.cookies.get("access_token") or None
    return access_token


@router.post("/logout")
async def logout_user(
        response: Response,
):
    response.delete_cookie("access_token")
    return {"status": "OK"}