from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from crud.setting import setting_service
from crud.user import user_service
from crud.order import order_service
from models.transaction import Transaction
from schemas.pagination import Pagination
from schemas.transaction import TransactionBase, VerifyTransaction, VerifyTransactionReq, VerifyTransactionRes, createTransaction
from external_services.payment_service import Payment
from services.payments.factory import PaymentFactory

class TransactionService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, page: int, size: int, current_user: int) -> List[TransactionBase]:
        query = self.db.query(Transaction).filter_by(user_id=current_user).order_by(Transaction.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get(self, transaction_id: int, current_user: int) -> TransactionBase:
        transaction_item: TransactionBase = self.db.query(Transaction).filter_by(id=transaction_id, user_id=current_user).first()
        if not transaction_item:
            raise HTTPException(status_code=404, detail="transaction not found!")
        return transaction_item
    
    def create(self, transaction_in: createTransaction, current_user: int):
        transaction_item = Transaction(
                order_id = transaction_in.order_id,
                user_id = current_user,
                payment_method_id = transaction_in.payment_method_id,
                transaction_type = transaction_in.transaction_type, 
                description = transaction_in.description,
                amount = transaction_in.amount,
            )
        self.db.add(transaction_item)
        self.db.commit()
        self.db.refresh(transaction_item)
        return transaction_item.id
        
    def update(self, transaction_id: int, transaction_in: createTransaction, current_user: int):
        transaction_item: TransactionBase = self.get(transaction_id, current_user)

        transaction_item.payment_method_id = transaction_in.payment_method_id
        transaction_item.transaction_type = transaction_in.transaction_type
        transaction_item.description = transaction_in.description
        transaction_item.amount = transaction_in.amount
        transaction_item.status = transaction_in.status
        
        self.db.commit()
        self.db.refresh(transaction_item)
    
    def delete(self, transaction_id: int, current_user: int):
        transaction_item: TransactionBase = self.get(transaction_id, current_user)
        if transaction_item.order_id:
            raise HTTPException(status_code=400, detail="Can't delete this transaction!")
        self.db.delete(transaction_item)
        self.db.commit()
    
    def pay(self, transaction_id: int, current_user: int):
        
        transaction_item: TransactionBase = self.get(transaction_id, current_user)
        
        payment_method_code = 'online' if transaction_item.transaction_type == 'wallet_deposit' else None
        if not payment_method_code:
            setting_value = setting_service.get_value(self.db, 'payment_methods')
            payment_methods = setting_value['payment_methods']
            payment_method_code = next((item['code'] for item in payment_methods if item['id'] == transaction_item.payment_method_id), None)
        
        if not payment_method_code:
            raise HTTPException(status_code=400, detail="Payment method not configured")
        
        strategy = PaymentFactory.get_strategy(self.db, payment_method_code)
        if not strategy:
            raise HTTPException(status_code=400, detail="Unsupported payment method")
        
        data = {"current_user": current_user}
        
        try:
            pay_response = strategy.handle_payment(transaction_item, data)
            self.db.commit()
            self.db.refresh(transaction_item)
            return pay_response
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    def verify(self, verify_data: VerifyTransactionReq, current_user: int):
        transaction_item: TransactionBase = self.db.query(Transaction).options(joinedload(Transaction.order)).filter_by(res_number=verify_data.res_number, user_id=current_user).first()
        if not transaction_item:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        verify_data = VerifyTransaction(
            status=verify_data.status,
            res_number=verify_data.res_number,
            amount=transaction_item.amount
        )
        payment_service = Payment()
        verify_response: VerifyTransactionRes = payment_service.verify_pay(verify_data)
        
        transaction_item.status = verify_response.status
        transaction_item.portal_out = datetime.now()
        transaction_item.ref_id = verify_response.ref_id
        transaction_item.fee = verify_response.fee
        transaction_item.fee_type = verify_response.fee_type
        
        # اگر تراکنش مربوط به شارژ کیف پول باشد، موجودی کاربر افزایش می‌یابد
        if transaction_item.transaction_type == "wallet_deposit":
            user = user_service.get(self.db, transaction_item.user_id)
            user.balance += transaction_item.amount
        
        if transaction_item.transaction_type == "order":
            # Finalize reserved products and set order status to processing
            # Assuming you have a method to finalize products and update order status
            order_service.finalize_order(self.db, transaction_item.order_id)

        try:
            self.db.commit()
            self.db.refresh(transaction_item)
            return transaction_item
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
