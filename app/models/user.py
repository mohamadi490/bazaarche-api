
from .base import Base
from sqlalchemy import Column, Numeric, Table, ForeignKey, DateTime, Integer, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'))
    password = Column(String)
    is_active = Column(Boolean, default=True)
    birth_date = Column(DateTime, nullable=True)
    balance = Column(Numeric(20, 0), default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    products = relationship("Product", back_populates="user")
    carts = relationship("Cart", back_populates="user")
    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="customer")
    transactions = relationship("Transaction", back_populates="user")

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    tag = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")
    
class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")

# Association table for many-to-many relationship between Role and Permission
role_permission = Table('role_permission', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)