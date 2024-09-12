from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UsersSchemas(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UsersAdd(UsersSchemas):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UsersCreate(UsersSchemas):
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_superuser: bool = False


class User(UsersSchemas):
    id: int
    email: EmailStr
    first_name: str
    last_name: str