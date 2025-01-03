from fastapi import APIRouter, Depends, Query
from starlette import status
from core.security import get_current_user
from core.database import get_db
from sqlalchemy.orm import Session
from crud.product import product_service
from schemas.product import ProductBase, Product, ProductConfig, ProductCreate, ProductUpdate, Products, SimpleProduct, ProductList
from schemas.result import PaginationResult, Result
from typing import List

from schemas.user import UserBase

product_router = APIRouter(
    prefix='/products',
    tags=['products']
)

@product_router.get("/", response_model=PaginationResult[List[Products]], status_code=status.HTTP_200_OK)
async def get_products(product_config: ProductConfig, db: Session = Depends(get_db)):
    items, pagination = product_service.get_list(db, product_config)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد!')


@product_router.get("/{product_slug}", response_model=Result[Product], status_code=status.HTTP_200_OK)
async def get_info(product_slug: str, db: Session = Depends(get_db)):
    product_item = product_service.get(db=db, product_slug=product_slug)
    return Result(isDone=True, data=product_item, message='عملیات با موفقیت انجام شد!')