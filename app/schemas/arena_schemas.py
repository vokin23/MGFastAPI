from typing import List
from datetime import datetime
from pydantic import BaseModel


class MSGArenaSchema(BaseModel):
    steam_id: str
    msg: str


class ArenaCreateSchema(BaseModel):
    name: str
    description: str
    cords_spawn: List[dict]
    cloths: List[dict]
    free: bool


class ArenaBaseSchema(ArenaCreateSchema):
    id: int


class ArenaRegPlayerSchema(BaseModel):
    steam_id: str
    items: List[dict]
    position: str
    orientation: str


class ArenaDeleteRegPlayerSchema(BaseModel):
    steam_id: str


class MatchReturnSchema(BaseModel):
    cords_spawn: List[dict]
    cloths1: List[dict]
    player1: str
    cloths2: List[dict]
    player2: str


class DeleteRegArenaSchema(BaseModel):
    steam_id: str
