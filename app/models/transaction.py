from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from .base import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    payment_method_id = Column(Integer, nullable=True)
    transaction_type = Column(Enum("order", "wallet_deposit", "wallet_withdraw", name="transaction_type"), nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Numeric(20,0), nullable=False)
    status = Column(Enum("success", "failed", "pending", "canceled", name="transaction_status"), default="pending")
    res_number = Column(String, nullable=True)
    ref_id = Column(Integer, nullable=True)
    fee = Column(Integer, nullable=True)
    fee_type = Column(String, nullable=True)
    portal_in = Column(DateTime, nullable=True)
    portal_out = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    order = relationship("Order", back_populates="transactions")
    user = relationship("User", back_populates="transactions")