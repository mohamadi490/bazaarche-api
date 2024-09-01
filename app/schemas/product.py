
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from schemas.category import SimpleCategory
from schemas.media import Image, ImageBase, ProductImage, ProductImage
from schemas.user import SimpleUser
from schemas.attribute import *

class VariationBase(BaseModel):
    sku: str
    cost_price: int
    price: int
    final_price: int
    quantity: int
    low_stock_threshold: int
    status: str
        
class Variation(VariationBase):
    id: int

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
    category_ids: List[int]
    attributes: List[ProductAttributeCreate]
    images: List[ImageBase]
    variations: List[VariationBase]

class ProductUpdate(ProductBase):
    category_ids: List[int]
    attributes: List[ProductAttributeUpdate]
    images: List[ProductImage]
    variations: List[Variation]
    deleted_image_ids: List[int]
    deleted_attr_ids: List[int]
    deleted_var_ids: List[int]

class Product(ProductBase):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    categories: Optional[List[SimpleCategory]]
    attributes: Optional[List[ProductAttribute]]
    variations: Optional[List[Variation]]
    files: Optional[List[ProductImage]]
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
    files: Optional[List[ImageBase]]
    user: SimpleUser

    class Config:
        orm_mode = True