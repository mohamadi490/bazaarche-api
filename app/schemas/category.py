
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    slug: str
    type: Optional[str]
    description: Optional[str] = None
    
class SimpleCategory(BaseModel):
    id: int
    name: str
    slug: str
    type: Optional[str]
    parent_id:  Optional[int]

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class Category(CategoryBase):
    id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True