from fastapi import APIRouter, Depends, Query
from starlette import status
from db.base import get_db
from sqlalchemy.orm import Session
from crud.product import product_service
from schemas.product import ProductBase, Product, ProductCreate, SimpleProduct, ProductList
from schemas.result import PaginationResult, Result
from typing import List

product_router = APIRouter(
    prefix='/products',
    tags=['products']
)

@product_router.get("/", response_model=PaginationResult[List[ProductList]], status_code=status.HTTP_200_OK)
async def get_products(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    items, pagination = product_service.get_all(db, page, size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد!')

@product_router.get("/{product_slug}", response_model=Result[Product])
async def get_product(product_slug: str, db: Session = Depends(get_db)):
    product_item = product_service.get(db=db, product_slug=product_slug)
    return Result(isDone=True, data=product_item, message='عملیات با موفقیت انجام شد!')

@product_router.post("/create", response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    product_service.create(db=db, product_in=product_in)
    return Result(isDone=True, data=None, message='محصول با موفقیت ایجاد شد')