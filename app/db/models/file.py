from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import DeclarativeBase

class FileBase(DeclarativeBase):
    pass

class File(FileBase):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    alt = Column(String)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    is_thumbnail = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime)
    
    # composite index for faster querying
    __table_args__ = (Index('idx_entity_type_id', 'entity_type', 'entity_id'),)