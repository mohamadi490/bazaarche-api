from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, DateTime, Numeric, String, Enum, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import and_
from db.base import Base
from .image import Image
import enum

class ProductType(enum.Enum):
    Simple = 'simple'
    Variable = 'variable'
    
class InventoryStatus(enum.Enum):
    InStock = 'in_stock'
    OutOfStock = 'out_of_stock'
    PreOrder = 'pre_order'
    BackOrder = 'back_order'
    
class Status(enum.Enum):
    PUBLISHED = 'published'
    DRAFT = 'draft'
    PENDING = 'pending'
        

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
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
    categories = relationship("Category", secondary="product_categories")
    tags = relationship("Tag", secondary="product_tags")
    
    @declared_attr
    def images(cls):
        return relationship(
            "Image",
            primaryjoin=lambda: and_(
                Image.entity_id == cls.id,
                Image.entity_type == 'product'
            ),
            foreign_keys=[Image.entity_id, Image.entity_type],
            cascade="all, delete-orphan"
        )

    @property
    def thumbnail(self):
        return next((img for img in self.images if img.is_thumbnail), None)

class ProductVariation(Base):
    __tablename__ = 'product_variations'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product_attribute_id = Column(Integer, ForeignKey('product_attributes.id'), nullable=True)
    sku = Column(String(64), unique=True, nullable=False)
    cost_price = Column(Numeric(20, 0), nullable=True)
    price = Column(Numeric(20, 0), nullable=False)
    final_price = Column(Numeric(20, 0), nullable=False)
    quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=5)
    status = Column(Enum(InventoryStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    product = relationship("Product", back_populates="variations")
    product_attribute = relationship("ProductAttribute")

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
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attributes.id'), nullable=False)
    value = Column(String)
    show_top = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime)
    
    product = relationship('Product', back_populates='attributes')
    attribute = relationship('Attribute', back_populates='products')


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(String)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime)
    
    products = relationship('Product', secondary="product_categories", back_populates='categories')
    parent = relationship('Category', remote_side=[id], backref=backref('children', cascade='all, delete-orphan'))
    
class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime)
    
    products = relationship('Product', secondary="product_tags", back_populates='tags')


product_categories = Table('product_categories', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

product_tags = Table('product_tags', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)