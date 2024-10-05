from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, insert

from app.models.datebase import async_session_maker
from app.models.player_model import Player


bot_router = APIRouter(prefix="/bot")
admin_router = APIRouter(prefix="/bot")


