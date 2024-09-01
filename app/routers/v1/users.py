from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import get_current_user
from core.database import get_db
from models.user import User
from schemas.user import FullUser, UserBase, UserCreate, UserUpdate
from starlette import status
from crud.user import user_service
from typing import List
from schemas.result import Result

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/", response_model=Result[List[FullUser]], status_code=status.HTTP_200_OK)
async def get_users(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    users = user_service.get_all(db)
    return Result(isDone=True, data=users, message='')

@router.get("/{user_id}", response_model=Result[FullUser], status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = user_service.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found!')
    return Result(isDone=True, data=user, message='')

@router.post("/create", response_model=Result[None], status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_in.email:
        user = user_service.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
    if user_in.phone_number:
        user = user_service.get_by_phone_number(db, phone_number=user_in.phone_number)
        if user:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    user_service.create(db, user_in=user_in)
    return Result(isDone=True, data=None, message='user created successfully')

@router.put("/update/{user_id}", response_model=Result[None], status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = user_service.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.update(db, db_user=user, user_in=user_in)
    return Result(isDone=True, data=None, message='user updated successfully')

@router.delete("/delete/{user_id}", response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = user_service.get(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user_service.remove(db, user_id=user_id)
    return Result(isDone=True, data=None, message='user deleted successfully')