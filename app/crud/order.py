import json
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from models import Order, OrderItem
from models.cart import CartItem
from models.order import OrderStatus
from models.product import Product
from models.setting import Setting
from models.user import User
from schemas.pagination import Pagination
from schemas.order import CreateOrder, UpdateOrder
from crud.cart import cart_service

class OrderService:
    def get_all(self, db: Session, page: int, size: int):
        query = db.query(Order).options(
            joinedload(Order.order_items),
            joinedload(Order.customer).load_only(User.id, User.username),
        ).order_by(Order.created_at.desc()).with_entities(
            Order.id,
            Order.customer,
            Order.final_price,
            Order.status,
            Order.created_at
        )
        query = query.add_columns(
            db.query(OrderItem).filter(OrderItem.order_id == Order.id).count()
        )
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get(self, db: Session, order_id: int):
        pass
    
    def add_order_item(self, db: Session, cart_item: CartItem, order_id: int) -> OrderItem:
        product = db.query(Product).filter(Product.id == cart_item.variation.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {cart_item.variation.product_id} not found")
        
        order_item = OrderItem(
            order_id=order_id,
            product_id=product.id,
            product_name=product.name,
            product_metadata=json.dumps(cart_item.variation.id),
            quantity=cart_item.variation.quantity,
            unit_price=cart_item.variation.price,
            total_price=cart_item.variation.price * cart_item.variation.quantity,
        )
        return order_item
    
    def create(self, db: Session, current_user: int):
        # Validate and retrieve the cart
        cart_service.validate(db, current_user)
        cart = cart_service.get_cart(db, current_user)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Calculate total price
        total_price = sum(item.total_price for item in cart.cart_items)

        # Check for existing pending order
        existing_order = db.query(Order).filter(
            Order.customer_id == current_user,
            Order.status == OrderStatus.PENDING
        ).first()

        if existing_order:
            # Update the existing order
            existing_order.order_total = total_price
            existing_order.final_price = total_price

            # Remove existing order items
            db.query(OrderItem).filter(OrderItem.order_id == existing_order.id).delete()
            order_id = existing_order.id
        else:
            # Create a new order
            new_order = Order(
                customer_id=current_user,
                order_total=total_price,
                final_price=total_price,
                status=OrderStatus.PENDING,
            )
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            order_id = new_order.id

        # Add new order items to db
        for item in cart.cart_items:
            new_order_item = self.add_order_item(db, item, order_id)
            db.add(new_order_item)

        db.commit()
        
    
    def admin_create(self, db: Session, data: CreateOrder):
        pass
        
    def update(self, db: Session, data: UpdateOrder, current_user: int):
        
        cart_service.validate(db, current_user)
        
        order = db.query(Order).filter(
            Order.customer_id == current_user,
            Order.status == "pending"
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        tax_amount = 0
        tax = db.query(Setting).filter_by(key='tax').first()
        if tax:
            tax_amount = (int(json.loads(tax.value)) * order.order_total) / 100
        
        order.address_id = data.address_id
        order.shipping_id = data.shipping_id
        order.shipping_cost = data.shipping_cost
        order.tax_amount = tax_amount
        order.final_price = order.order_total + data.shipping_cost + tax_amount
        
        db.commit()
        db.refresh(order)
        
        return order.id
    
    def delete(self, db: Session, order_id: int):
        pass

    
order_service = OrderService()