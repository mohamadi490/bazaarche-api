
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(100), nullable=True)
    
    cities = relationship("City", order_by=id, back_populates="country")

class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(100), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)

    country = relationship("Country", back_populates="cities")

class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    postal_code = Column(String(20), nullable=False)
    phone_number = Column(String(11), nullable=True)
    line_1 = Column(String(255), nullable=False)
    line_2 = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="addresses")  # Assuming a User model exists
    city = relationship("City")
    country = relationship("Country")