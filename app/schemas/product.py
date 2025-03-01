
from datetime import datetime
from typing import List
from pydantic import BaseModel
from schemas.category import SimpleCategory
from schemas.media import ImageBase, ProductImage
from schemas.pagination import paginationConfig
from schemas.user import SimpleUser
from schemas.attribute import *

class VariationAttributes(BaseModel):
    attribute_id: int
    value: str

class VariationAttributesResponse(BaseModel):
    name: str
    value: str

class VariationBase(BaseModel):
    sku: str
    cost_price: int
    unit_price: int
    sales_price: int
    weight: Optional[int] = None
    quantity: int
    low_stock_threshold: int
    status: str

class VariationCreate(VariationBase):
    variation_attributes: List[VariationAttributes]
        
class Variation(VariationBase):
    id: int
    variation_attributes: List[VariationAttributesResponse]

class VariationUpdate(VariationBase):
    id: Optional[int] = None
    variation_attributes: List[VariationAttributes]

class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    featured: Optional[bool] = False

class SimpleProduct(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    body: Optional[str] = None
    category_ids: List[int]
    attributes: List[ProductAttributeCreate]
    files: List[ImageBase]
    variations: List[VariationCreate]
    status: str

class ProductUpdate(ProductBase):
    body: Optional[str] = None
    category_ids: List[int]
    attributes: List[ProductAttributeUpdate]
    files: Optional[List[ProductImage]] = None
    variations: List[VariationUpdate]
    deleted_image_ids: Optional[List[int]] = None
    deleted_attr_ids: Optional[List[int]] = None
    deleted_var_ids: Optional[List[int]] = None
    status: str

class Product(ProductBase):
    id: Optional[int]
    type: str
    body: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    categories: Optional[List[SimpleCategory]]
    attributes: Optional[List[ProductAttribute]]
    variations: Optional[List[Variation]]
    files: Optional[List[ProductImage]]
    user: SimpleUser
    status: str

    class Config:
        orm_mode = True

class ProductList(ProductBase):
    id: Optional[int]
    type: str
    sku: Optional[str] = ''
    unit_price: Optional[int] = 0
    sales_price: Optional[int] = 0
    quantity: Optional[int] = 0
    reserved_quantity: Optional[int] = 0
    var_status: Optional[str] = ''
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    categories: Optional[List[SimpleCategory]]
    files: Optional[List[ImageBase]]
    user: SimpleUser
    status: str

    class Config:
        orm_mode = True

class Products(ProductBase):
    id: int
    thumbnail: Optional[ImageBase] = None
    unit_price: Optional[int] = 0
    sales_price: Optional[int] = 0
    quantity: Optional[int] = 0
    var_id: Optional[int] = None
    sku: Optional[str] = ''
    var_status: Optional[str] = ''
    categories: Optional[List[SimpleCategory]] = None

class ProductFilters(BaseModel):
    min_price: Optional[int] = 0
    max_price: Optional[int] = 0
    categories: Optional[List[SimpleCategory]] = None
    ordering_options: list[str]
    
class ProductListData(BaseModel):
    products: list[Products]
    filters: ProductFilters

class ProductVariation(BaseModel):
    id: int
    sku: str
    unit_price: int
    sales_price: int
    quantity: int
    status: str
    product: SimpleProduct


class AttributeSchema(BaseModel):
    id: int
    name: str
    

class ProductConfig(BaseModel):
    keyword:Optional[str] = None
    categories: Optional[list[int]] = None
    order_by: str = 'newest'
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    paginate: paginationConfig

class AdminProductSearchParams(BaseModel):
    name: Optional[str] = None          # جستجو بر اساس نام محصول
    sku: Optional[str] = None           # جستجو بر اساس SKU محصول
    created_from: Optional[datetime] = None  # تاریخ شروع ایجاد محصول (برای فیلترینگ بازه زمانی)
    created_to: Optional[datetime] = None    # تاریخ پایان ایجاد محصول
    categories: Optional[List[int]] = None     # لیست شناسه دسته‌بندی‌ها جهت فیلتر کردن

class AdminProductsRequest(BaseModel):
    order_by: Optional[str] = "created_at"   # ستون مرتب‌سازی (مثلاً: created_at, name, sales_price)
    order_dir: Optional[str] = "desc"         # جهت مرتب‌سازی (asc یا desc)
    search_params: Optional[AdminProductSearchParams] = None  # پارامترهای جستجو و فیلترینگ
    paginate: paginationConfig