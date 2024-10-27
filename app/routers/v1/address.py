
from fastapi import APIRouter, Depends
from requests import Session

from core.database import get_db
from core.security import get_current_user
from crud.address import address_service
from schemas.address import UserAddress, UserAddressBase, UserAddressCreate
from schemas.result import Result

address_router = APIRouter(
    prefix='/addresses',
    tags=['addresses']
)

@address_router.get('/', response_model=Result[list[UserAddress]])
async def get_address_list(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    data = address_service.get_user_adresses(db=db, user_id=current_user)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@address_router.get('/{address_id}', response_model=Result[UserAddressBase])
async def get_address(address_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    data = address_service.get_address(db=db, address_id=address_id, current_user=current_user)
    return Result(isDone=True, data=data, message='عملیات با موفقیت انجام شد')

@address_router.post('/create', response_model=Result[None])
async def create_address(address_in: UserAddressCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    address_service.create_address(db=db, address_in=address_in, current_user=current_user)
    return Result(isDone=True, data=None, message='آدرس با موفقیت ایجاد شد')

@address_router.post('/update/{address_id}', response_model=Result[None])
async def update_address(address_id: int, address_in: UserAddressCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    address_service.update_address(db=db, address_id=address_id, address_in=address_in, current_user=current_user)
    return Result(isDone=True, data=None, message='آدرس با موفقیت ویرایش شد')

@address_router.delete('/delete/{address_id}', response_model=Result[None])
async def delete_address(address_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    address_service.delete_address(db=db, address_id=address_id, current_user=current_user)
    return Result(isDone=True, data=None, message='آدرس با موفقیت حذف شد')