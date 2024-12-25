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

class CreateOrder(BaseModel):
    customer_id: int
    order_total: int
    final_price: int
    items: List[OrderItemSchema]

    class Config:
        orm_mode = True

class UpdateOrder(BaseModel):
    address_id: int
    shipping_id: int
    shipping_cost: int
    payment_method_id: int
