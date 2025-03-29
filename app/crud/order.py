import json
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from crud.product import product_service
from crud.cart import cart_service
from crud.setting import setting_service
from models import Order, OrderItem, OrderStatus, CartItem, User
from schemas.pagination import Pagination
from schemas.order import CreateOrder


class OrderService:
    def get_all(self, db: Session, page: int, size: int):
        # تعریف یک scalar subquery جهت محاسبه تعداد آیتم‌های سفارش به ازای هر Order
        items_count_subq = (
            db.query(func.count(OrderItem.id))
              .filter(OrderItem.order_id == Order.id)
              .correlate(Order)
              .scalar_subquery()
        )

        # کوئری اصلی جهت دریافت سفارشات همراه با اطلاعات مشتری و تعداد آیتم‌ها
        query = db.query(Order).options(
                  joinedload(Order.customer),
                  joinedload(Order.order_items)
              ).order_by(Order.created_at.desc()).add_columns(items_count_subq.label('items_count'))

        # صفحه‌بندی کوئری
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        results = paginated_query.all()

        # پردازش نتایج: هر نتیجه یک tuple شامل (Order, items_count) است.
        orders = []
        for order, items_count in results:
            orders.append({
                "id": order.id,
                "customer": {
                    "id": order.customer.id,
                    "username": order.customer.username,
                } if order.customer else None,
                "final_price": order.final_price,
                "status": order.status,
                "created_at": order.created_at,
                "items_count": items_count if items_count is not None else 0,
                # سایر فیلدهای مورد نیاز سفارش را می‌توانید اضافه کنید
            })

        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return orders, pagination
    
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
        tax = setting_service.get_value(db, 'tax')
        if tax:
            tax_amount = (int(tax) * cart.total_amount) / 100

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

        # Reserve quantity of product_variation and add new order items to db
        for cart_item in cart.cart_items:
            product_service.reserve_quantity(db, cart_item.variation_id, cart_item.quantity)
            new_order_item = self.add_order_item(db, cart_item, new_order.id)
            db.add(new_order_item)

        db.commit()
        
        # clear cart
        # cart_service.delete_cart_items(db, current_user)
        
        return new_order
        
    
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
    
    def finalize_order(self, db: Session, order_id: int):
        # Assuming you have an Order model and a way to get the order by transaction_id
        order = db.query(Order).filter_by(id=order_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found!")

        # Finalize reserved products
        for item in order.order_items:
            variation_id = json.loads(item.product_metadata)
            product_service.finalize_reserved_quantity(db, variation_id, item.quantity)
            

        # Update the order status to processing
        order.status = OrderStatus.PROCESSING
        db.add(order)  # Add the updated order back to the session

    
order_service = OrderService()