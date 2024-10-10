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
    position: List[str]
    orientation: List[str]


class ArenaDeleteRegPlayerSchema(BaseModel):
    steam_id: str


# class CordsSpawnSchema(BaseModel):
#     position: List[str]
#     orientation: List[str]


class MatchReturnSchema(BaseModel):
    cords_spawn: list
    cloths1: List[dict]
    player1: str
    cloths2: List[dict]
    player2: str


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
