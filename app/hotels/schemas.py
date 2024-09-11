from pydantic import BaseModel


class HotelsSchemas(BaseModel):
    title: str
    name: str
