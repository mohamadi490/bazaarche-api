from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.security import create_access_token
from core.utils import utils
from crud.auth import auth_service
from core.database import get_db
from schemas.result import Result
from schemas.auth import BaseAuth, LoginRequest, RegisterRequest, Token
from starlette import status

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post('/panel', response_model=Token)
def panel_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='اطلاعات وارد شده اشتباه است')
    token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


@router.post("/verify", response_model=Result)
def verify(auth_validate: BaseAuth, db: Session = Depends(get_db)):
    username_type = utils.get_username_type(auth_validate.username)
    if not username_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="نام کاربری وارد شده معتبر نیست")
    user = auth_service.verify_user(db, auth_validate.username, username_type)
    data = {
        "type": username_type,
        "username": auth_validate.username,
        "step": "register" if not user else "login",
        "hasPassword": bool(user and user.password)
    }
    return Result(isDone=True, data=data, message='درخواست با موفقیت انجام شد')


@router.post("/send_code", response_model=Result, status_code=status.HTTP_200_OK)
def send_code(phone_number: str, db: Session = Depends(get_db)):
    response = auth_service.send_code(db, phone_number)
    if not response:
        raise HTTPException(status_code=500, detail="ارسال پیام با خطا مواجه شد")
    return Result(isDone=True, message="پیام با موفقیت ارسال شد")


@router.post("/login", response_model=Result, status_code=status.HTTP_200_OK)
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    username_type = utils.get_username_type(login_in.username)
    user = auth_service.login(db, login_in, username_type)
    return Result(isDone=True, data=user, message='درخواست با موفقیت انجام شد')


@router.post("/register", response_model=Result, status_code=status.HTTP_200_OK)
def register(register_in: RegisterRequest, db: Session = Depends(get_db)):
    username_type = utils.get_username_type(register_in.username)
    token_data = auth_service.register(db, register_in, username_type)
    return Result(isDone=True, data=token_data, message='درخواست با موفقیت انجام شد')