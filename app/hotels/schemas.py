from pydantic import BaseModel, Field


class HotelsSchemas(BaseModel):
    class Config:
        orm_mode = True


class HotelsPost(HotelsSchemas):
    title: str
    location: str


class HotelsPut(HotelsSchemas):
    title: str
    name: str


class HotelsPatch(HotelsSchemas):
    title: str | None = Field(None)
    name: str | None = Field(None)
