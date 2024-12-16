from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class ShippingBase(BaseModel):
    name: str
    description: str
    estimated_days: int
    is_active: bool

class ShippingAreaItem(BaseModel):
    id: int
    city_ids: Optional[List[int]] = None
    price: int

class ShippingItem(ShippingBase):
    id: int
    created_at: datetime

class ShippingMethodData(ShippingBase):
    areas: List[ShippingAreaItem]

class MethodItem(ShippingBase):
    id: int
    price: int