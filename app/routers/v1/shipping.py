
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from crud.shipping import shipping_service
from core.database import get_db
from schemas.shipping import ShippingMethodData, ShippingItem, MethodItem
from schemas.result import PaginationResult, Result
from starlette import status

shipping_router = APIRouter(
    prefix='/shippings',
    tags=['shippings']
)

@shipping_router.get('/', response_model=PaginationResult[List[ShippingItem]])
async def get_all(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    items, pagination = shipping_service.get_all(db=db, page=page, size=size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد')

@shipping_router.get('/methods', response_model=Result[List[MethodItem]])
async def get_methods(db: Session = Depends(get_db), province_id: int = Query(ge=1), city_id: int = Query(ge=1)):
    data = shipping_service.get_methods(db=db, province_id=province_id, city_id=city_id)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@shipping_router.get('/{shipping_id}', response_model=Result[ShippingMethodData])
async def get_shipping(shipping_id: int, db: Session = Depends(get_db)):
    data = shipping_service.get(db=db, shipping_id=shipping_id)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@shipping_router.post('/create', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_shipping(data: ShippingMethodData, db: Session = Depends(get_db)):
    shipping_service.create(db=db, data=data)
    return Result(isDone=True, data=None, message='روش ارسال با موفقیت ایجاد شد')

@shipping_router.put('/update/{method_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def update_shipping(method_id: int, data: ShippingMethodData, db: Session = Depends(get_db)):
    shipping_service.update(db=db, method_id=method_id, data=data)
    return Result(isDone=True, data=None, message='روش ارسال با موفقیت ویرایش شد')

@shipping_router.delete('/delete/{method_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_shipping(method_id: int, db: Session = Depends(get_db)):
    shipping_service.delete(db=db, method_id=method_id)
    return Result(isDone=True, data=None, message='روش ارسال با موفقیت حذف شد')

@shipping_router.delete('/delete-all/', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_all(db: Session = Depends(get_db)):
    shipping_service.delete_all(db=db)
    return Result(isDone=True, data=None, message='روش های ارسال با موفقیت حذف شدند')