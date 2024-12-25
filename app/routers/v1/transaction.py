
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.security import get_current_user
from crud.transaction import transaction_service
from core.database import get_db
from schemas.transaction import TransactionBase, createTransaction
from schemas.result import PaginationResult, Result
from starlette import status
from schemas.user import UserBase

transaction_router = APIRouter(
    prefix='/transactions',
    tags=['transactions']
)

@transaction_router.get('/', response_model=PaginationResult[List[TransactionBase]])
async def get_all(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1), current_user: UserBase = Depends(get_current_user)):
    items, pagination = transaction_service.get_all(db=db, page=page, size=size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد')

@transaction_router.get('/{transaction_id}', response_model=Result[TransactionBase])
async def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    data = transaction_service.get(db=db, transaction_id=transaction_id)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@transaction_router.post('/create', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_in: createTransaction, db: Session = Depends(get_db)):
    transaction_service.create(db=db, transaction_in=transaction_in, current_user=1)
    return Result(isDone=True, data=None, message='تراکنش با موفقیت ایجاد شد')

@transaction_router.put('/update/{transaction_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def update_transaction(transaction_id: int, transaction_in: createTransaction, db: Session = Depends(get_db)):
    transaction_service.update(db=db, transaction_id=transaction_id, transaction_in=transaction_in)
    return Result(isDone=True, data=None, message='تراکنش با موفقیت ویرایش شد')

@transaction_router.delete('/delete/{transaction_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_transaction(order_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    transaction_service.delete(db=db, order_id=order_id)
    return Result(isDone=True, data=None, message='تراکنش با موفقیت حذف شد')

@transaction_router.post('/pay', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def pay_transaction(transaction_id: int, callback_url: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    transaction_service.pay(db=db, transaction_id=transaction_id, callback_url=callback_url)
    return Result(isDone=True, data=None, message='عملیات با موفقیت انجام شد')

@transaction_router.get('/verify', response_model=Result[TransactionBase])
async def verify_transaction(ref_number: str, status: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    data = transaction_service.verify(db=db, ref_number=ref_number, status=status)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

