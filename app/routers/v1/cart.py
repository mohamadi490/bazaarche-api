from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from crud.cart import cart_service
from schemas.cart import Cart
from schemas.result import Result

cart_router = APIRouter(
    prefix='/carts',
    tags=['carts']
)

@cart_router.get('/', response_model=Result[Cart])
async def get_cart(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    cart = cart_service.get_cart(db=db, user_id=current_user)
    if not cart:
        cart = cart_service.create_cart(db=db, user_id=current_user)
    return Result(isDone=True, data=cart, message='عملیات با موفقیت انجام شد')

@cart_router.post('/add', response_model=Result[Cart])
async def add_cart_item(variation_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    cart = cart_service.add_cart_item(db=db, current_user=current_user, variation_id=variation_id)
    return Result(isDone=True, data=cart, message='عملیات با موفقیت انجام شد')

@cart_router.post('/update', response_model=Result[Cart])
async def update_cart_item(cart_item_id: int, operation: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    cart = cart_service.update_cart_item(db=db, item_id=cart_item_id, operation=operation)
    return Result(isDone=True, data=cart, message='عملیات با موفقیت انجام شد')

@cart_router.delete('/delete', response_model=Result[None])
async def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    cart_service.delete_cart_item(db=db, item_id=cart_item_id)
    return Result(isDone=True, data=None ,message='عملیات با موفقیت انجام شد')

@cart_router.delete('/delete_all', response_model=Result[None])
async def delete_cart_items(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    cart_service.delete_cart_items(db=db, current_user=current_user)
    return Result(isDone=True, data=None, message='عملیات با موفقیت انجام شد')
