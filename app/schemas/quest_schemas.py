from typing import List
from datetime import datetime
from pydantic import BaseModel, Field


class ReputationTypeBaseSchema(BaseModel):
    id: int
    name: str
    description: str
    static: bool


class ReputationTypeCreateSchema(BaseModel):
    name: str
    description: str
    static: bool


class OperatorBaseSchema(BaseModel):
    id: int
    name: str
    description: str
    class_name: str
    reputation_type_id: int
    position: str
    orientation: str
    clothes: List[str]


class OperatorCreateSchema(BaseModel):
    name: str
    description: str
    class_name: str
    reputation_type_id: int
    position: str
    orientation: str
    clothes: List[str]


class AwardsSchema(BaseModel):
    classname: str
    count: int


class ConditionSchema(BaseModel):
    condition_name: str
    progress: str
    need: str


class RequiredItemsSchema(BaseModel):
    classname: str
    count: int


class QuestBaseSchema(BaseModel):
    id: int
    name: str
    type: str
    title: str
    description: str
    awards: List[AwardsSchema]
    awards_api: int | None
    conditions: List[ConditionSchema]
    required_items: List[RequiredItemsSchema] | None
    operator_id: int
    reputation_need: int
    reputation_add: int
    reputation_minus: int


class QuestCreateSchema(BaseModel):
    name: str
    type: str
    title: str
    description: str
    awards: List[AwardsSchema]
    awards_api: int = Field(None, alias="awards_api")
    conditions: List[ConditionSchema]
    required_items: List[RequiredItemsSchema] = Field(None, alias="required_items")
    operator_id: int
    reputation_need: int
    reputation_add: int
    reputation_minus: int


class ActivityCreateSchema(BaseModel):
    steam_id: str
    quest_id: int


class ActivityBaseSchema(BaseModel):
    id: int
    player_id: int
    quest_id: int
    conditions: List[ConditionSchema]
    is_active: bool
    is_completed: bool
    award_take: bool

    class Config:
        from_attributes = True


class MSGSchema(BaseModel):
    steam_id: str
    msg: str


class PDAInfoSchema(BaseModel):
    steam_id: str
    activities: List[ActivityBaseSchema]
    reputation: list
    vip_lvl: str


class UpdateActivitySchema(BaseModel):
    steam_id: str
    data: dict


class AwardListSchema(BaseModel):
    classname: str
    count: int


class QuestCompleteResponseSchema(BaseModel):
    steam_id: str
    activity_id: int


class QuestCompleteSchema(BaseModel):
    steam_id: str
    msg: str
    award: List[AwardListSchema]
