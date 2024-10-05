from pydantic import BaseModel


class UpdateVipStatus(BaseModel):
    steam_id: str
    vip_lvl: int
    days: int
