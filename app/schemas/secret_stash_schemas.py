from typing import List

from pydantic import BaseModel, Field, ConfigDict


class SecretStashSchema(BaseModel):
    id: int
    class_name: str
    position: str
    orientation: str
    category_id: int
    is_opened: bool = False


class SecretStashCreateSchema(BaseModel):
    class_name: str
    position: str
    orientation: str
    category_id: int
    is_opened: bool = False


class Award(BaseModel):
    class_name: str
    value: int


class StashOpenSchema(BaseModel):
    stash_id: int
    steam_id: str


class SecretStashOpenSchema(BaseModel):
    steam_id: str
    msg: str
    awards: List[Award]


class SecretStashCategorySchema(BaseModel):
    id: int
    name: str
    description: str
    filling: int
    awards_list: list[dict[str, int]]


class SecretStashCategoryCreate(BaseModel):
    name: str
    description: str
    filling: int
    awards_list: list[dict[str, int]]


class SecretStashCategoryPatch(BaseModel):
    name: str | None
    description: str | None
    filling: int | None
    awards_list: list[dict[str, int]] | None


class SecretStashPatch(BaseModel):
    class_name: str | None
    position: str | None
    orientation: str | None
    category_id: int | None
    is_opened: bool | None
