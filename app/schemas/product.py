
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from schemas.category import SimpleCategory

from schemas.user import SimpleUser

class ImageBase(BaseModel):
    url: HttpUrl
    alt: Optional[str] = None
    is_thumbnail: bool = False
    order: int
    
class Image(ImageBase):
    id: int
    entity_type: str
    entity_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
    

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
        
class Variation(BaseModel):
    id: int
    sku: str
    cost_price: int
    price: int
    final_price: int
    quantity: int
    low_stock_threshold: int
    status: str

class ProductBase(BaseModel):
    name: str
    slug: str
    type: str
    description: Optional[str] = None
    body: Optional[str] = None
    featured: Optional[bool] = False
    status: str

class SimpleProduct(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    user_id: int
    category_ids: List[int]
    attributes: List[ProductAttributeCreate]
    images: List[ImageBase]
    variations: List[Variation]

class Product(ProductBase):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    categories: Optional[List[SimpleCategory]]
    attributes: Optional[List[ProductAttribute]]
    variations: Optional[List[Variation]]
    images: Optional[List[Image]]
    user: SimpleUser

    class Config:
        orm_mode = True

class ProductList(ProductBase):
    id: Optional[int]
    sku: Optional[str] = ''
    price: Optional[int] = 0
    final_price: Optional[int] = 0
    quantity: Optional[int] = 0
    var_status: Optional[str] = ''
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    categories: Optional[List[SimpleCategory]]
    images: Optional[List[Image]]
    user: SimpleUser

    class Config:
        orm_mode = True