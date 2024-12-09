from datetime import datetime
from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class ShippingMethod(Base):
    __tablename__ = 'shipping_methods'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    base_cost = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    estimated_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    shipping_areas = relationship("ShippingArea", back_populates="shipping_method")

class ShippingArea(Base):
    __tablename__ = "shipping_areas"
    id = Column(Integer, primary_key=True)
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id"), nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    price_modifier = Column(Float, nullable=True)

    shipping_method = relationship("ShippingMethod")
    province = relationship("Province")
    city = relationship("City")


