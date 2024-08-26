from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str | None
    email: EmailStr | None
    phone_number: str
    first_name: str | None
    last_name: str | None
    role_id: int

class SimpleUser(BaseModel):
    id: int
    username: str | None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str = None
    is_active: bool = True

class UserInDBBase(UserBase):
    id: int

    class Config:
        orm_mode = True

class FullUser(UserInDBBase):
    created_at: datetime
    updated_at: datetime

class UserInDB(UserInDBBase):
    hashed_password: str
