from typing import List
from datetime import datetime
from pydantic import BaseModel


class ReputationSchema(BaseModel):
    name: str
    level: int


class PlayerSchema(BaseModel):
    id: int
    steam_id: str
    game_balance: int
    site_balance: int
    vip: bool
    vip_lvl: int
    reputation: List[ReputationSchema]
    created_at_player: datetime
    created_at_vip: str | None
    date_end_vip: str | None


class PlayerCreateSchema(BaseModel):
    steam_id: str


class PlayerUpdateSchema(BaseModel):
    game_balance: int
    site_balance: int
    vip: bool
    vip_lvl: int
    reputation: List[ReputationSchema]
    created_at_vip: str | None
    date_end_vip: str | None


class PlayerPatchSchema(BaseModel):
    game_balance: int | None
    site_balance: int | None
    vip: bool | None
    vip_lvl: int | None
    reputation: List[ReputationSchema] | None
    created_at_vip: str | None
    date_end_vip: str | None


class PlayerGetGameBalanceSchema(BaseModel):
    steam_id: str
    balance: str
