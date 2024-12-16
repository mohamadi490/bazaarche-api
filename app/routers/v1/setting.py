from typing import List
from fastapi import APIRouter, Depends
from core.database import get_db
from crud.setting import setting_service
from sqlalchemy.orm import Session
from schemas.result import Result
from schemas.setting import SettingBase, SettingItem
from starlette import status

setting_router = APIRouter(
    prefix='/settings',
    tags=['settings']
)

@setting_router.get('/', response_model=Result[List[SettingBase]])
async def get_all(db: Session = Depends(get_db)):
    data = setting_service.get_all(db)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@setting_router.get('/{setting_id}', response_model=Result[SettingItem])
async def get(setting_id: int, db: Session = Depends(get_db)):
    data = setting_service.get(db, setting_id)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@setting_router.post('/create', response_model=Result[None], status_code=status.HTTP_201_CREATED)
async def create(data: SettingBase, db: Session = Depends(get_db)):
    setting_service.create(db, data)
    return Result(isDone=True, data=None, message='عملیات با موفقیت انجام شد')

@setting_router.put('/update/{setting_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def update(setting_id: int, data: SettingItem, db: Session = Depends(get_db)):
    setting_service.update(db, data, setting_id)
    return Result(isDone=True, data=None, message='عملیات با موفقیت انجام شد')

@setting_router.delete('/delete/{setting_id}', response_model=Result[None], status_code=status.HTTP_200_OK)
async def delete(setting_id: int, db: Session = Depends(get_db)):
    setting_service.delete(db, setting_id)
    return Result(isDone=True, data=None, message='عملیات با موفقیت انجام شد')