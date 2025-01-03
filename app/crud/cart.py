from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from core.exceptions import CustomHTTPException
from models.cart import Cart, CartItem
from models.product import ProductVariation
from starlette import status

class CartService:
    
    def get_cart(self, db: Session, user_id: int) -> Cart:
        return db.query(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.cart_items)).first()
    
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
        cart = self.get_cart(db=db, user_id=current_user)
        if variation_id in [item.variation_id for item in cart.cart_items]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='آیتم درون کارت وجود دارد')
        total_price = float(self.get_variation_total_price(db=db, variation_id=variation_id, quantity=1))
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
            if variation.quantity > item.quantity:
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
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='امکان کمتر کردن تعداد محصول وجود ندارد')
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='لطفا نوع عملیات را به درستی ارسال کنید')
        db.commit()
        db.refresh(item)
        return item.cart

    def delete_cart_item(self, db: Session, item_id: int) -> bool:
        item = db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='آیتم مورد نظر پیدا نشد')
        db.delete(item)
        item.cart.total_amount -= item.total_price
        db.commit()
        return item.cart
    
    def delete_cart_items(self, db: Session, current_user: int):
        cart = self.get_cart(db=db, user_id=current_user)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='سبد خریدی برای این کاربر پیدا نشد')
        # cart.created_at = cart.created_at.isoformat()
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
    
    def validate(self, db: Session, user_id: int):

        cart = db.query(Cart).options(joinedload(Cart.cart_items)).filter(Cart.user_id == user_id).first()
        
        if not cart:
            raise CustomHTTPException(status_code=404, message="Cart not found")

        # Fetch all product variations in one query
        variation_ids = [item.variation_id for item in cart.cart_items]
        product_variations = db.query(ProductVariation).filter(ProductVariation.id.in_(variation_ids)).all()
        variation_map = {pv.id: pv for pv in product_variations}

        unvalidated_items = []
        for item in cart.cart_items:
            product_variation = variation_map.get(item.variation_id)
            if not product_variation:
                unvalidated_items.append({
                    "product_id": None,
                    "product_name": None,
                    "variation_id": item.variation_id,
                    "message": "Product Variation not found"
                })
                continue

            if product_variation.quantity < item.quantity:
                unvalidated_items.append({
                    "product_id": product_variation.product_id,
                    "product_name": product_variation.product.name,
                    "variation_id": product_variation.id,
                    "message": "Not enough stock"
                })

            if product_variation.final_price != item.total_price / item.quantity:
                unvalidated_items.append({
                    "product_id": product_variation.product_id,
                    "product_name": product_variation.product.name,
                    "variation_id": product_variation.id,
                    "message": "Price changed"
                })
        
        if len(unvalidated_items) > 0:
            raise CustomHTTPException(status_code=400, message="Cart validation failed", data={"errors": unvalidated_items})
        
        return True
        
        


# Initialize the cart service
cart_service = CartService()
