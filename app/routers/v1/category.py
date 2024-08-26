
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from crud.category import category_service
from db.base import get_db
from schemas.category import Category, CategoryBase, CategoryCreate
from schemas.result import PaginationResult, Result
from starlette import status


category_router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@category_router.get('/', response_model=PaginationResult[List[Category]])
async def get_all(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    items, pagination = category_service.get_all(db=db, page=page, size=size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد')


@category_router.get('/{category_id}', response_model=Result[CategoryBase])
async def get_category(category_id: int, db: Session = Depends(get_db)):
    data = category_service.get(db=db, category_id=category_id)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')


@category_router.post('/create', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    category_service.create(db=db, cat_in=category_in)
    return Result(isDone=True, data=None, message='دسته بندی با موفقیت ایجاد شد')


@category_router.put('/update/{category_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category_in: CategoryCreate, db: Session = Depends(get_db)):
    category_service.update(db=db, category_id=category_id, category_in=category_in)
    return Result(isDone=True, data=None, message='دسته بندی با موفقیت ویرایش شد')


@category_router.delete('/delete/{category_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_service.delete(db=db, category_id=category_id)
    return Result(isDone=True, data=None, message='دسته بندی با موفقیت حذف شد')