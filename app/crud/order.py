import json
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from crud.product import product_service
from crud.cart import cart_service
from models import Order, OrderItem, OrderStatus, CartItem, Setting, User
from schemas.pagination import Pagination
from schemas.order import CreateOrder, UpdateOrder


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
        product_item = product_service.get_by_id(db, cart_item.variation.product_id)
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_item.id,
            product_name=product_item.name,
            product_metadata=json.dumps(cart_item.variation.id),
            quantity=cart_item.quantity,
            unit_price=cart_item.variation.sales_price,
            total_price=cart_item.total_price,
        )
        return order_item
    
    def create(self, db: Session, current_user: int):
        # Validate and retrieve the cart
        cart = cart_service.validate(db, current_user)

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

        # Reserve quantity of product_variation and add new order items to db
        for cart_item in cart.cart_items:
            product_service.reserve_quantity(db, cart_item.variation_id, cart_item.quantity)
            new_order_item = self.add_order_item(db, cart_item, order_id)
            db.add(new_order_item)

        db.commit()
        
    
    def admin_create(self, db: Session, data: CreateOrder):
        pass
        
    def update(self, db: Session, data: UpdateOrder, current_user: int):
        # Validate and retrieve the cart
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