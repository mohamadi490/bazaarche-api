from sqlalchemy import JSON, Boolean, Column, Integer, String
from .base import Base

class Setting(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)