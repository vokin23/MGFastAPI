from typing import List
from datetime import datetime
from pydantic import BaseModel

class MSGArenaSchema(BaseModel):
    steam_id: str
    msg: str


class CordSchema(BaseModel):
    position: str
    orientation: str


class ClothsSchema(BaseModel):
    head: str
    body: str
    legs: str
    feet: str
    glovers: str
    backpack: str
    items: List[str]


class ArenaCreateSchema(BaseModel):
    name: str
    description: str
    cords_spawn: List[CordSchema] | None
    cloths: List[ClothsSchema] | None
    status: bool


class ArenaBaseSchema(ArenaCreateSchema):
    id: int



class ArenaPutSchema(BaseModel):
    name: str
    description: str
    cords_spawn: List[CordSchema]
    cloths: List[ClothsSchema]
    status: bool


class ArenaPatchSchema(BaseModel):
    name: str | None
    description: str | None
    cords_spawn: List[CordSchema] | None
    cloths: List[ClothsSchema] | None
    status: bool | None


class MatchBaseSchema(BaseModel):
    id: int
    arena: int | None
    player1: int | None
    old_things_player1: List[ClothsSchema] | None
    new_things_player1: List[ClothsSchema] | None
    player2: int | None
    old_things_player2: List[ClothsSchema] | None
    new_things_player2: List[ClothsSchema] | None
    time_created: datetime
    time_start: datetime | None = None
    time_end: datetime | None = None
    start: bool
    finished: bool
    winner: int | None

class MatchReturnSchema(MatchBaseSchema):
    cords_spawn: List[CordSchema]
    player1: str
    player2: str
    cloths_player1: ClothsSchema
    cloths_player2: ClothsSchema




