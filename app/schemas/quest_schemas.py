from typing import List
from datetime import datetime
from pydantic import BaseModel


class AwardAPIBaseSchema(BaseModel):
    id: int
    method: str
    type: str
    name: str
    count: int


class AwardSchema(BaseModel):
    classname: str
    count: int


class RequiredItemsSchema(BaseModel):
    classname: str
    count: int


class ConditionSchema(BaseModel):
    action: str
    condition_name: str
    progress: int
    need: int


class ReputationTypeBase(BaseModel):
    id: int
    name: str
    description: str
    static: bool


class ReputationTypeCreate(BaseModel):
    name: str
    description: str
    static: bool


class ReputationTypePatch(BaseModel):
    name: str | None
    description: str | None


class OperatorBase(BaseModel):
    id: int
    admin_name: str
    name: str
    description: str
    class_name: str
    reputation_type: int
    position: str
    orientation: str
    clothes: list


class OperatorCreate(BaseModel):
    admin_name: str
    name: str
    description: str
    class_name: str
    reputation_type: int
    position: str
    orientation: str
    clothes: dict


class OperatorPatch(BaseModel):
    admin_name: str | None
    name: str | None
    description: str | None
    class_name: str | None
    reputation_type: int | None
    position: str | None
    orientation: str | None
    clothes: dict | None


class QuestBase(BaseModel):
    id: int
    name: str
    type: str
    title: str
    description: str
    awards: List[AwardSchema] | None
    awards_api: List[AwardAPIBaseSchema] | None
    conditions: List[ConditionSchema]
    required_items: List[RequiredItemsSchema] | None
    operator: int
    reputation_need: int
    reputation_add: int
    reputation_minus: int


class QuestCreate(BaseModel):
    name: str
    type: str
    title: str
    description: str
    awards: List[AwardSchema] | None
    awards_api: List[AwardAPIBaseSchema] | None
    conditions: List[ConditionSchema]
    required_items: List[RequiredItemsSchema] | None
    operator: int
    reputation_need: int
    reputation_add: int
    reputation_minus: int


class QuestPatch(BaseModel):
    name: str | None
    type: str | None
    title: str | None
    description: str | None
    awards: List[AwardSchema] | None
    awards_api: List[AwardAPIBaseSchema] | None
    conditions: List[ConditionSchema] | None
    required_items: List[RequiredItemsSchema] | None
    operator: int | None
    reputation_need: int | None
    reputation_add: int | None
    reputation_minus: int | None


class ActivityBase(BaseModel):
    id: int
    player: int
    quest: int
    conditions: List[ConditionSchema]
    is_active: bool
    is_completed: bool
    award_take: bool
    changed_at: str


class QuestResponseForPlayer(BaseModel):
    steam_id: int
    quests: List[QuestBase]


class QuestCompletionResponse(BaseModel):
    steam_id: str
    msg: str
    award: List[AwardSchema]


class ActivityCreate(BaseModel):
    steam_id: str
    msg: str


class RepForPDASchema(BaseModel):
    name: str
    level: str


class PDASchema(BaseModel):
    steam_id: str
    activity: List[ActivityBase]
    reputation: List[RepForPDASchema]
    vip: int
