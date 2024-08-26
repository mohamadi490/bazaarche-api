from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declared_attr
from db.base import Base

class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    alt = Column(String)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    is_thumbnail = Column(Boolean, default=False)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime)
    
    # composite index for faster querying
    __table_args__ = (Index('idx_entity_type_id', 'entity_type', 'entity_id'),)
    
    # # polymorphic relationship
    # @declared_attr
    # def entity(cls):
    #     return {
    #         'polymorphic_on': cls.entity_type,
    #     }