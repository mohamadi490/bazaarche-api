from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from .base import Base
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    shipping_id = Column(Integer, ForeignKey("shipping_methods.id"), nullable=False)
    shipping_cost = Column(Numeric(20,0), default=0)
    tax_amount = Column(Numeric(20,0), default=0)
    order_total = Column(Numeric(20,0), nullable=False)
    final_price = Column(Numeric(20,0), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    customer = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="order", cascade="all, delete-orphan")
    

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(20,0), nullable=False)
    total_price = Column(Numeric(20,0), nullable=False)  # unit_price * quantity
    product_metadata = Column(String, nullable=True)
    
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")