import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models.user import User
from core.security import verify_password
from core.utils import utils

class AuthService:
    def verify_user(self, db: Session, username: str, username_type: str):
        if username_type == 'phone_number':
            user = db.query(User).filter(User.phone_number == username).first()
        elif username_type == 'email':
            user = db.query(User).filter(User.email == username).first()
        else:
            raise HTTPException(status_code=400, detail="Invalid username")
        return user
    
    def check_username_type(self, username: str):
        if utils.is_phone_number(username):
            return 'phone_number'
        elif utils.is_email(username):
            return 'email'
        else:
            return ''


auth_service = AuthService()
