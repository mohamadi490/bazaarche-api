import json
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from crud.product import product_service
from crud.cart import cart_service
from models import Order, OrderItem, OrderStatus, CartItem, Setting, User
from schemas.pagination import Pagination
from schemas.order import CreateOrder


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
            unit_price=cart_item.variation.unit_price,
            sales_price=cart_item.variation.sales_price
        )
        return order_item
    
    def create(self, db: Session, order_in: CreateOrder, current_user: int):
        # Validate and retrieve the cart
        cart = cart_service.validate(db, current_user)
        
        # Determine the tax amount based on the total amount of the cart if tax exist
        tax_amount = 0
        tax = db.query(Setting).filter_by(key='tax').first()
        if tax:
            tax_amount = (int(json.loads(tax.value)) * cart.total_amount) / 100

        # Create a new order
        new_order = Order(
            customer_id = current_user,
            address_id = order_in.address_id,
            shipping_id = order_in.shipping_id,
            shipping_cost = order_in.shipping_cost,
            tax_amount = tax_amount,
            order_total = cart.total_amount,
            final_price = cart.total_amount + order_in.shipping_cost + tax_amount,
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
        
        # clear cart
        # cart_service.delete_cart_items(db, current_user)
        
        return order_id
        
    
    def admin_create(self, db: Session, data: CreateOrder):
        pass
        
    def update(self, db: Session, current_user: int):
        # Validate and retrieve the cart
        cart_service.validate(db, current_user)
        
        order = db.query(Order).filter(
            Order.customer_id == current_user,
            Order.status == "pending"
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        db.commit()
        db.refresh(order)
        
        return order.id
    
    def delete(self, db: Session, order_id: int):
        pass

    
order_service = OrderService()