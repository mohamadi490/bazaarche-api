from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from models.cart import Cart, CartItem
from models.product import ProductVariation
from starlette import status

class CartService:
    
    def get_cart(self, db: Session, user_id: int) -> Cart:
        return db.query(Cart).options(joinedload(Cart.cart_items)).filter(Cart.user_id == user_id).first()
    
    def create_cart(self, db: Session, user_id: int) -> Cart:
        new_cart = Cart(user_id=user_id, total_amount=0.0)  # Initialize total_amount to 0
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart
          
    def delete_cart(self, db: Session, user_id: int) -> bool:
        cart = self.get_cart(db=db, user_id=user_id)
        if not cart:
            return False
        db.delete(cart)
        db.commit()
        return True
    
    def add_cart_item(self, db: Session, current_user: int, variation_id: int) -> Cart:
        cart_item = db.query(CartItem).filter(CartItem.variation_id == variation_id).first()
        if cart_item:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='آیتم درون کارت وجود دارد')
        total_price = float(self.get_variation_total_price(db=db, variation_id=variation_id, quantity=1))
        cart = self.get_cart(db=db, user_id=current_user)
        cart.total_amount += total_price
        new_item = CartItem(cart_id=cart.id, variation_id=variation_id, quantity=1, total_price=total_price)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return cart

    def update_cart_item(self, db: Session, item_id: int, operation: str) -> CartItem:
        item = db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='آیتم مورد نظر پیدا نشد')
        variation = db.query(ProductVariation).filter(ProductVariation.id == item.variation_id).first()
        if operation == '+':
            if variation.quantity > item.quantity + 1:
                item.quantity += 1
                item.total_price += float(variation.final_price)
                item.cart.total_amount += float(variation.final_price)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='تعداد محصولات انتخابی بیشتر از موجودی است')
        elif operation == '-':
            if item.quantity > 1:
                item.quantity -= 1
                item.total_price -= float(variation.final_price)
                item.cart.total_amount -= float(variation.final_price)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='امکان کمتر کردن وجود ندارد')
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='لطفا نوع عملیات را به درستی ارسال کنید')
        db.commit()
        db.refresh(item)
        return item.cart

    def delete_cart_item(self, db: Session, item_id: int) -> bool:
        item = db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        item.cart.total_amount -= item.total_price
        db.commit()
        return item.cart
    
    def delete_cart_items(self, db: Session, current_user: int):
        cart = self.get_cart(db=db, user_id=current_user)
        if not cart:
            return False
        for item in cart.cart_items:
            db.delete(item)
        cart.total_amount = 0
        db.commit()
        return cart
        
    def get_variation_total_price(self, db: Session, variation_id: int, quantity: int) -> float:
        if variation_id:
            variation = db.query(ProductVariation).filter(ProductVariation.id == variation_id).first()
            if variation:
                return variation.final_price * quantity
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='متغیر انتخابی پیدا نشد')
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='شناسه متغیر اجباری می باشد')


# Initialize the cart service
cart_service = CartService()
