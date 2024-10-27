from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud.user import user_service
from schemas.auth import LoginRequest, RegisterRequest
from models.user import User
from core.security import verify_password
from external_services.sms_service import send_sms
from crud.verification_code import verification_code_service as vc_service
from core.security import create_access_token

class AuthService:
    
    def authenticate_user(self, username: str, password: str, db: Session):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user
    
    def verify_user(self, db: Session, username: str, username_type: str):
        if username_type == 'phone_number':
            user = db.query(User).filter(User.phone_number == username).first()
        elif username_type == 'email':
            user = db.query(User).filter(User.email == username).first()
        return user
        
    def send_code(self, db: Session, phone_number: str):
        verification_code = vc_service.create_verification_code(db=db, phone_number=phone_number)
        response = send_sms(phone_number=phone_number, code=verification_code.code)
        return response
 
    
    def login(self, db: Session, login_in: LoginRequest, username_type: str):
        user = self.verify_user(db, username=login_in.username, username_type=username_type)
        if not user:
            raise HTTPException(status_code=404, detail="کاربری با شماره موبایل یا ایمیل وارد شده یافت نشد")
        if login_in.hasPassword:
            if not verify_password(login_in.password, user.password):
                raise HTTPException(status_code=401, detail="کلمه عبور اشتباه است")
        else:
            verification_code = vc_service.get_valid_code(db, login_in.username, login_in.password)
            if not verification_code:
                raise HTTPException(status_code=401, detail="کد پیدا نشد")
        # make a jwt token and send to user
        token_data = create_access_token(user.id)
        return token_data
    
    def register(self, db: Session, register_in: RegisterRequest):
        verification_code = vc_service.get_valid_code(db=db, phone_number=register_in.username, code=register_in.password)
        if not verification_code:
            raise HTTPException(status_code=401, detail="کد پیدا نشد")
        # mark the code as used
        vc_service.mark_code_as_used(db, verification_code.id)
        # create a user with given number
        user = user_service.create_quick(db, register_in.username)
        token_data = create_access_token(user.id)
        return token_data
    

auth_service = AuthService()
