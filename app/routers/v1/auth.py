from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from crud.auth import auth_service
from core.database import get_db
from schemas.result import Result
from schemas.auth import BaseAuth, LoginRequest, RegisterRequest, Token, UserToken
from starlette import status

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth_router.post("/verify", response_model=Result)
def verify(auth_validate: BaseAuth, db: Session = Depends(get_db)):
    data = auth_service.verify(db, auth_validate.username)
    return Result(isDone=True, data=data, message='درخواست با موفقیت انجام شد')

@auth_router.post("/send_code", response_model=Result, status_code=status.HTTP_200_OK)
def send_code(phone_number: str, db: Session = Depends(get_db)):
    auth_service.send_code(db, phone_number)
    return Result(isDone=True, message="پیام با موفقیت ارسال شد")

@auth_router.post("/login", response_model=Result[UserToken], status_code=status.HTTP_200_OK)
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    data = auth_service.login(db, login_in)
    return Result(isDone=True, data=data, message='درخواست با موفقیت انجام شد')

@auth_router.post("/register", response_model=Result[UserToken], status_code=status.HTTP_200_OK)
def register(register_in: RegisterRequest, db: Session = Depends(get_db)):
    data = auth_service.register(db, register_in)
    return Result(isDone=True, data=data, message='درخواست با موفقیت انجام شد')

@auth_router.post('/admin', response_model=Result[UserToken])
def panel_login(login_in: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    data = auth_service.panel_login(db, login_in)
    return Result(isDone=True, data=data, message='درخواست با موفقیت انجام شد')

@auth_router.post('/token', response_model=Token, include_in_schema=False)
def token(login_in: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    data = auth_service.panel_login(db, login_in, 'document')
    return data