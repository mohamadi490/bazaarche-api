from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from schemas.user import SimpleUser

class OrderBase(BaseModel):
    final_price: int
    status: str

class OrderListSchema(OrderBase):
    id: int
    customer: SimpleUser
    items_count: int
    created_at: datetime

class OrderItemSchema(BaseModel):
    product_id: int
    product_name: str
    product_metadata: str
    quantity: int
    unit_price: int
    sales_price: int

class CreateOrder(BaseModel):
    address_id: int
    shipping_id: int
    shipping_cost: int

    class Config:
        orm_mode = True
    
class OrderResponse(BaseModel):
    id: int
    final_price: int
    status: str

class UpdateOrder(BaseModel):
    address_id: int
    shipping_id: int
    shipping_cost: int
    payment_method_id: int
