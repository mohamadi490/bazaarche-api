
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, root_validator


class AttributeBase(BaseModel):
    name: str
    
class Attribute(AttributeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProductAttributeBase(BaseModel):
    value: str
    show_top: bool = False

class ProductAttributeCreate(ProductAttributeBase):
    attribute_id: int

class ProductAttributeUpdate(ProductAttributeCreate):
    id: Optional[int] = None
    
class ProductAttribute(ProductAttributeBase):
    id: int
    attribute_id: int
    name: str
    
    @root_validator(pre=True)
    def extract_attribute_name(cls, values):
        attr = values.attribute
        if attr:
            if hasattr(attr, 'name'):
                values.name = attr.name
            if hasattr(attr, 'attribute_id'):
                values.attribute_id = attr.attribute_id
        return values

    class Config:
        orm_mode = True