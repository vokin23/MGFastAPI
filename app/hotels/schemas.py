from pydantic import BaseModel, Field, ConfigDict


class HotelsSchemas(BaseModel):
    class Config:
        orm_mode = True


class HotelsPost(HotelsSchemas):
    title: str
    location: str


class Hotel(HotelsPost):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HotelsPut(HotelsSchemas):
    title: str
    location: str


class HotelsPatch(HotelsSchemas):
    title: str | None = Field(None)
    name: str | None = Field(None)
