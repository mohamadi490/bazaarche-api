from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from .base import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_type = Column(Enum("order_online", "order_wallet", "order_cash", "wallet_deposit", "wallet_withdraw", name="transaction_type"), nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Numeric(20,0), nullable=False)
    status = Column(Enum("success", "failed", "pending", name="transaction_status"), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    order = relationship("Order", back_populates="transactions")
    user = relationship("User", back_populates="transactions")