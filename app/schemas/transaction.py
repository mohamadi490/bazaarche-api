from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.order import OrderItemSchema


class TransactionBase(BaseModel):
    order_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    transaction_type: str
    description: str
    res_number: Optional[str] = None
    ref_id: Optional[int] = None
    amount: int
    status: str

class transaction_order(TransactionBase):
    order: OrderItemSchema
    
    
class TransactionSchema(TransactionBase):
    id: int
    created_at: datetime


class createTransaction(BaseModel):
    order_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    transaction_type: str
    description: str
    amount: Optional[int] = None

class PayTransactionRes(BaseModel):
    status_code: int
    payment_url: str
    res_number: str
 
class VerifyTransactionReq(BaseModel):
    status: str
    res_number: str

class VerifyTransaction(VerifyTransactionReq):
    amount: int

class VerifyTransactionRes(BaseModel):
    status: str
    ref_id: Optional[int] = None
    fee: Optional[int] = None
    fee_type: Optional[str] = None