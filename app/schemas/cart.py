from typing import List
from pydantic import BaseModel

from schemas.product import ProductVariation


class CartItem(BaseModel):
    id: int
    variation: ProductVariation
    quantity: int
    total_price: float

class Cart(BaseModel):
    id: int
    total_amount: int
    cart_items: List[CartItem]
    
    class Config:
        orm_mode = True