from fastapi import APIRouter, Depends, Query
from starlette import status
from core.security import get_current_user
from core.database import get_db
from sqlalchemy.orm import Session
from crud.product import product_service
from schemas.product import ProductBase, Product, ProductCreate, ProductUpdate, SimpleProduct, ProductList
from schemas.result import PaginationResult, Result
from typing import List

from schemas.user import UserBase

admin_product_router = APIRouter(
    prefix='/products',
    tags=['admin/products']
)

@admin_product_router.get("/", response_model=PaginationResult[List[ProductList]], status_code=status.HTTP_200_OK)
async def get_products(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1), current_user: UserBase = Depends(get_current_user)):
    items, pagination = product_service.get_all(db, page, size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد!')


@admin_product_router.get("/{product_slug}", response_model=Result[Product], status_code=status.HTTP_200_OK)
async def get_product(product_slug: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    product_item = product_service.get(db=db, product_slug=product_slug)
    return Result(isDone=True, data=product_item, message='عملیات با موفقیت انجام شد!')


@admin_product_router.post("/create", response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    product_service.create(db=db, product_in=product_in, current_user=current_user)
    return Result(isDone=True, data=None, message='محصول با موفقیت ایجاد شد')


@admin_product_router.put("/update/{product_slug}", response_model=Result[None], status_code=status.HTTP_200_OK)
async def update_product(product_in: ProductUpdate, product_slug: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    product_service.update(db=db, product_in=product_in, product_slug=product_slug, current_user=current_user)
    return Result(isDone=True, data=None, message='محصول با موفقیت ویرایش شد')


@admin_product_router.delete("/delete/{product_slug}", response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete_product(product_slug: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    product_service.delete(db=db, product_slug=product_slug, current_user=current_user)
    return Result(isDone=True, data=None, message='محصول با موفقیت حذف شد')