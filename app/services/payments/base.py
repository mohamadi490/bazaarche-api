from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from external_services.payment_service import Payment
from crud.user import user_service

class PaymentStrategy:
    def __init__(self, db: Session):
        self.db = db
        
    def handle_payment(self, transaction_item, data = None):
        raise NotImplementedError

class OnlinePayment(PaymentStrategy):
    def handle_payment(self, transaction_item, data = None):
        # اتصال به درگاه آنلاین
        payment_service = Payment()
        pay_response = payment_service.request_pay(int(transaction_item.amount), transaction_item.description)
        transaction_item.portal_in = datetime.now()
        transaction_item.res_number = pay_response.res_number
        return pay_response

class WalletPayment(PaymentStrategy):
    def handle_payment(self, transaction_item, data = None):
        # استفاده از موجودی کیف پول
        user = user_service.get(self.db, data.current_user)
        if user.balance > transaction_item.amount:
            user.balance -= transaction_item.amount
            transaction_item.status = "completed"
        else:
            raise HTTPException(status_code=400, detail="مقدار موجودی کیف پول کافی نیست!")