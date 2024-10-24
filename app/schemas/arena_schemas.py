from typing import List
from datetime import datetime
from pydantic import BaseModel


class MSGArenaSchema(BaseModel):
    steam_id: str
    msg: str


class ArenaGunsSchema(BaseModel):
    classname: str
    mag_classname: str
    mag_count: int
    attachments: List[str]


class ArenaClothsSchema(BaseModel):
    items: List[str]
    equipment: List[str]
    guns: List[ArenaGunsSchema]


class ArenaCreateSchema(BaseModel):
    name: str
    description: str
    cords_spawn: List[dict]
    cloths: List[ArenaClothsSchema]
    free: bool


class ArenaBaseSchema(ArenaCreateSchema):
    id: int


class ArenaRegPlayerSchema(BaseModel):
    steam_id: str
    items: dict
    position: str
    orientation: str


class ArenaDeleteRegPlayerSchema(BaseModel):
    steam_id: str


class MatchReturnSchema(BaseModel):
    cords_spawn1: dict
    cords_spawn2: dict
    cloths1: List[dict]
    player1: str
    cloths2: List[dict]
    player2: str


class ActionReturnSchema(BaseModel):
    game_data: List[MatchReturnSchema] | None
    message_data: List[MSGArenaSchema] | None


class DeleteRegArenaSchema(BaseModel):
    steam_id: str


class HistoryPlayerSchema(BaseModel):
    steam_id: str
    name: str
    surname: str
    fraction: str


class HistoryMatchSchema(BaseModel):
    players: List[HistoryPlayerSchema]
    winner: str


class PlayerInTopSchema(BaseModel):
    steam_id: str
    name: str
    surname: str
    fraction: str
    vip: bool
    arena_rating: int
    arena_rang: int
    KD: int
    win_rate: int
    max_win_streak: int
    matches: int
    history_matches: List[HistoryMatchSchema]


class StatsArePdaSchema(BaseModel):
    steam_id: str
    name: str
    surname: str
    fraction: str
    vip: bool
    arena_rating: int
    arena_rang: int
    KD: int
    win_rate: int
    max_win_streak: int
    matches: int
    history_matches: List[HistoryMatchSchema]
    tops: List[PlayerInTopSchema]


class PlayerInArenaQueueSchema(BaseModel):
    name: str
    surname: str


class OpenArenaMenuSchema(BaseModel):
    steam_id: str
    registration_required: bool
    queue_position: int | None
    players: List[PlayerInArenaQueueSchema] | None
    description: str | None
    arena_price: int | None
