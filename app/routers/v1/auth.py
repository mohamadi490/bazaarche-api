from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routers.dependencies import get_db
from crud.auth import auth_service
from schemas.result import Result
from schemas.auth import AuthValidate
# from schemas.user import UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/verify")
async def verify(auth_validate: AuthValidate, db: Session = Depends(get_db)):
    username_type = auth_service.check_username_type(auth_validate.username)
    data = {'type': username_type, 'username': auth_validate.username, 'step': '', 'hasPassword': False}
    user = auth_service.verify_user(db, auth_validate.username, username_type)
    if not user:
        data['step'] = 'register'
        return Result(isDone=True, data=data, message='')
    data['step'] = 'login'
    if user.password:
        data['hasPassword'] = True
        return Result(isDone=True, data=data, message='')
    return Result(isDone=True, data=data, message='')
