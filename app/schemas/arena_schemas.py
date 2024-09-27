from typing import List
from datetime import datetime
from pydantic import BaseModel


class MSGArenaSchema(BaseModel):
    steam_id: str
    msg: str


class CordSchema(BaseModel):
    position: str
    orientation: str


class ArenaCreateSchema(BaseModel):
    name: str
    description: str
    cords_spawn: List[CordSchema] | None
    cloths: List[str] | None
    status: bool


class ArenaBaseSchema(ArenaCreateSchema):
    id: int


class ArenaPutSchema(BaseModel):
    name: str
    description: str
    cords_spawn: List[CordSchema]
    cloths: List[str]
    status: bool


class ArenaPatchSchema(BaseModel):
    name: str | None
    description: str | None
    cords_spawn: List[CordSchema] | None
    cloths: List[str] | None
    status: bool | None


class MatchBaseSchema(BaseModel):
    id: int
    arena: int | None
    player1: int | None
    old_things_player1: List[str] | None
    new_things_player1: List[str] | None
    player2: int | None
    old_things_player2: List[str] | None
    new_things_player2: List[str] | None
    time_created: datetime
    time_start: datetime | None = None
    time_end: datetime | None = None
    start: bool
    finished: bool
    winner: int | None


class MatchReturnSchema(BaseModel):
    cords_spawn: List[CordSchema]
    player1: str
    player2: str
    cloths_player1: List[str]
    cloths_player2: List[str]
