from typing import List
from datetime import datetime
from pydantic import BaseModel


class ExpSchema(BaseModel):
    exp_id: int
    lvl: int
    progress: int


class ReputationSchema(BaseModel):
    name: str
    level: int


class PlayerSchema(BaseModel):
    id: int
    steam_id: str
    discord_name: str | None
    name: str
    surname: str
    avatar: str
    about: str
    survivor_model: str
    fraction_id: int
    prem_slot: bool
    game_balance: int
    site_balance: int
    vip: bool
    vip_lvl: int
    reputation: List[ReputationSchema]
    exp: List[ExpSchema]
    created_at_player: datetime
    created_at_vip: str | None
    date_end_vip: str | None
    arena_ranking: int
    kills: int
    deaths: int


class PlayerCreateSchema(BaseModel):
    steam_id: str


class PlayerUpdateSchema(BaseModel):
    discord_name: str | None
    name: str
    surname: str
    avatar: str
    about: str
    survivor_model: str
    fraction_id: int
    prem_slot: bool
    game_balance: int
    site_balance: int
    vip: bool
    vip_lvl: int
    reputation: List[ReputationSchema] | None
    exp: List[ExpSchema] | None
    created_at_vip: str | None
    date_end_vip: str | None
    arena_ranking: int
    kills: int
    deaths: int


class PlayerPatchSchema(BaseModel):
    discord_name: str | None
    name: str | None
    surname: str | None
    avatar: str | None
    about: str | None
    survivor_model: str | None
    fraction_id: int | None
    prem_slot: bool | None
    game_balance: int | None
    site_balance: int | None
    vip: bool | None
    vip_lvl: int | None
    reputation: List[ReputationSchema] | None
    exp: List[ExpSchema] | None
    created_at_vip: str | None
    date_end_vip: str | None
    arena_ranking: int
    kills: int
    deaths: int


class PlayerGetGameBalanceSchema(BaseModel):
    steam_id: str
    balance: str
