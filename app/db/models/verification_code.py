import random
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timedelta

class VerificationBase(DeclarativeBase):
    pass

class VerificationCode(VerificationBase):
    __tablename__ = 'verification_codes'
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, nullable=False)
    code = Column(String, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    
    @classmethod
    def create_code(cls, db, phone_number:str):
        code = cls.generate_code()
        expires_at = datetime.now() + timedelta(minutes=10)
        verification_code = cls(phone_number=phone_number, code=code, expires_at=expires_at)
        db.add(verification_code)
        db.commit()
        db.refresh(verification_code)
        return verification_code
    
    @staticmethod
    def generate_code() -> str:
        return str(random.randint(10000, 99999))


