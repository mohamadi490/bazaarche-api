import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, DateTime, Numeric, String, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import and_
from .file import File
from .base import Base

class ProductType(enum.Enum):
    SIMPLE = 'simple'
    VARIABLE = 'variable'
    
class InventoryStatus(enum.Enum):
    INSTOCK = 'in_stock'    
    OUTOFSTOCK = 'out_of_stock'
    PREORDER = 'pre_order'
    CALL = 'call'
    
class Status(enum.Enum):
    PUBLISHED = 'published'
    DRAFT = 'draft'
    PENDING = 'pending'
    
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    type = Column(Enum(ProductType), nullable=False)
    description = Column(String)
    body = Column(String)
    featured = Column(Boolean, default=False)
    status = Column(Enum(Status), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="products")
    variations = relationship("ProductVariation", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    categories = relationship('Category', secondary="product_categories")
    tags = relationship('Tag', secondary="product_tags")
    files = relationship("File", back_populates="product")
    
    @declared_attr
    def files(cls):
        return relationship(
            "File",
            primaryjoin=lambda: and_(
                File.entity_id == cls.id,
                File.entity_type == 'product'
            ),
            foreign_keys=[File.entity_id, File.entity_type],
            cascade="all, delete-orphan"
        )

    @property
    def thumbnail(self):
        return next((img for img in self.images if img.is_thumbnail), None)

class ProductVariation(Base):
    __tablename__ = 'product_variations'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    product_attribute_id = Column(Integer, ForeignKey('product_attributes.id', ondelete='CASCADE'), nullable=True)
    sku = Column(String(64), unique=True, nullable=False)
    cost_price = Column(Numeric(20, 0), nullable=True)
    unit_price = Column(Numeric(20, 0), nullable=False, default=0)
    sales_price = Column(Numeric(20, 0), nullable=False, default=0)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    weight = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=5)
    status = Column(Enum(InventoryStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    product = relationship("Product", back_populates="variations")
    product_attribute = relationship("ProductAttribute")
    cart_items = relationship("CartItem", back_populates="variation")

class Attribute(Base):
    __tablename__ = 'attributes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    products = relationship('ProductAttribute', back_populates='attribute')

class ProductAttribute(Base):
    __tablename__ = 'product_attributes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attributes.id', ondelete='CASCADE'), nullable=False)
    value = Column(String)
    show_top = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime)
    
    product = relationship('Product', back_populates='attributes')
    attribute = relationship('Attribute', back_populates='products')


product_categories = Table('product_categories', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

product_tags = Table('product_tags', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)