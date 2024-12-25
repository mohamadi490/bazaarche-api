
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.security import get_current_user
from crud.order import order_service
from core.database import get_db
from schemas.order import CreateOrder, UpdateOrder, OrderListSchema
from schemas.result import PaginationResult, Result
from starlette import status
from schemas.user import UserBase

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

@order_router.get('/', response_model=PaginationResult[List[OrderListSchema]])
async def get_all(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1), current_user: UserBase = Depends(get_current_user)):
    items, pagination = order_service.get_all(db=db, page=page, size=size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد')

@order_router.get('/{order_id}', response_model=Result[CreateOrder])
async def get_order(order_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    data = order_service.get(db=db, order_id=order_id)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@order_router.post('/create', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_order(db: Session = Depends(get_db)):
    order_service.create(db=db, current_user=1)
    return Result(isDone=True, data=None, message='سفارش با موفقیت ایجاد شد')

@order_router.put('/update', response_model=Result[None], status_code=status.HTTP_200_OK)
async def update_order(data: UpdateOrder, db: Session = Depends(get_db)):
    order_service.update(db=db, data=data, current_user=1)
    return Result(isDone=True, data=None, message='سفارش با موفقیت ویرایش شد')

@order_router.delete('/delete/{order_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_order(order_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    order_service.delete(db=db, order_id=order_id)
    return Result(isDone=True, data=None, message='سفارش با موفقیت حذف شد')