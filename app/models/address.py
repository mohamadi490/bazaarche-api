
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(100), nullable=True)
    
    Provinces = relationship("Province", order_by=id, back_populates="country")

class Province(Base):
    __tablename__ = 'provinces'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(100), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    
    country = relationship("Country", back_populates="Provinces")
    cities = relationship("City", order_by=id, back_populates="province")

class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(100), nullable=True)
    province_id = Column(Integer, ForeignKey('provinces.id'))
    
    province = relationship("Province", back_populates="cities")

class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    province_id = Column(Integer, ForeignKey('provinces.id'), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    title = Column(String(255), nullable=False)
    postal_code = Column(String(20), nullable=False)
    phone_number = Column(String(11), nullable=True)
    line_1 = Column(String(255), nullable=False)
    line_2 = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="addresses")  # Assuming a User model exists
    country = relationship("Country")
    province = relationship("Province")
    city = relationship("City")
    