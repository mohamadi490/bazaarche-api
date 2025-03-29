
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.security import get_current_user
from crud.transaction import TransactionService
from core.database import get_db
from schemas.transaction import PayTransactionRes, TransactionBase, TransactionSchema, VerifyTransactionReq, createTransaction, transaction_order
from schemas.result import PaginationResult, Result
from starlette import status
from schemas.user import UserBase

transaction_router = APIRouter(
    prefix='/transactions',
    tags=['transactions']
)

@transaction_router.get('/', response_model=PaginationResult[List[TransactionSchema]])
async def get_all(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    items, pagination = transaction_service.get_all(page, size, current_user)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد')

@transaction_router.get('/{transaction_id}', response_model=Result[TransactionBase])
async def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    data = transaction_service.get(transaction_id, current_user)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@transaction_router.post('/create', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_in: createTransaction, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    transaction_service.create(transaction_in, current_user)
    return Result(isDone=True, data=None, message='تراکنش با موفقیت ایجاد شد')

@transaction_router.put('/update/{transaction_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def update_transaction(transaction_id: int, transaction_in: createTransaction, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    transaction_service.update(transaction_id, transaction_in, current_user)
    return Result(isDone=True, data=None, message='تراکنش با موفقیت ویرایش شد')

@transaction_router.delete('/delete/{transaction_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    transaction_service.delete(transaction_id, current_user)
    return Result(isDone=True, data=None, message='تراکنش با موفقیت حذف شد')

@transaction_router.post('/pay/{transaction_id}', response_model=Result[PayTransactionRes], status_code=status.HTTP_201_CREATED)
async def pay_transaction(transaction_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    data = transaction_service.pay(transaction_id, current_user)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@transaction_router.post('/verify', response_model=Result[transaction_order])
async def verify_transaction(verify_data: VerifyTransactionReq, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    transaction_service = TransactionService(db)
    data = transaction_service.verify(verify_data, current_user)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

