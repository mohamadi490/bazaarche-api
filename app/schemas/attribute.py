
from datetime import datetime
from pydantic import BaseModel


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
    
class ProductAttribute(ProductAttributeBase):
    id: int
    product_id: int
    attribute: Attribute
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True