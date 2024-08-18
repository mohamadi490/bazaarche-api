from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.base import get_db
from schemas.role import RoleBase
from schemas.result import PaginationResult, Result
from crud.role import role_service
from typing import List
from crud.role import role_service
from starlette import status

role_router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)


@role_router.get("/", response_model=PaginationResult[List[RoleBase]], status_code=status.HTTP_200_OK)
async def get_roles(db: Session = Depends(get_db), page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    items, pagination = role_service.get_all_query(db, page, size)
    return PaginationResult(isDone=True, data=items, pagination=pagination, message='عملیات با موفقیت انجام شد!')


@role_router.get("/permissions", response_model=Result[List[str]], status_code=status.HTTP_200_OK)
async def get_permissions(db: Session = Depends(get_db)):
    permissions = role_service.get_permissions(db)
    return Result(isDone=True, data=permissions, message='عملیات با موفقیت انجام شد!')


@role_router.get("/{role_id}", response_model=Result[RoleBase], status_code=status.HTTP_200_OK)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    role = role_service.get(db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail='مقام مورد نظر یافت نشد!')
    return Result(isDone=True, data=role, message='عملیات با موفقیت انجام شد')
    

@role_router.post("/create", response_model=Result, status_code=status.HTTP_201_CREATED)
async def create_role(role_in: RoleBase, db: Session = Depends(get_db)):
    role_service.create(db, role_in)
    return Result(isDone=True, data=None, message='مقام با موفقیت ایجاد شد!')


@role_router.put("/update/{role_id}", response_model=Result, status_code=status.HTTP_200_OK)
async def update_role(role_id: int, role_in: RoleBase, db: Session = Depends(get_db)):
    role_service.update(db, role_id, role_in)
    return Result(isDone=True, data=None, message='مقام با موفقیت ویرایش شد!')


@role_router.delete("/delete/{role_id}", response_model=Result, status_code=status.HTTP_200_OK)
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    role_service.delete(db, role_id)
    return Result(isDone=True, data=None, message='مقام با موفقیت حذف شد!')