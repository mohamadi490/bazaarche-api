from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    role_id: int

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
