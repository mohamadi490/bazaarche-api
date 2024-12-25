from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.transaction import Transaction
from schemas.pagination import Pagination
from schemas.transaction import PayTransactionRes, TransactionBase, VerifyTransaction, VerifyTransactionRes
from external_services.payment_service import payment_service

class TransactionService:
    def get_all(self, db: Session, page: int, size: int):
        query = db.query(Transaction).order_by(Transaction.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get(self, db: Session, transaction_id: int):
        transaction_item = db.query(Transaction).filter_by(id=transaction_id).first()
        if not transaction_item:
            raise HTTPException(status_code=404, detail="transaction not found!")
        return transaction_item
    
    def create(self, db: Session, transaction_in: TransactionBase, current_user: int):
        transaction_item = Transaction(
                order_id = transaction_in.order_id,
                user_id = current_user,
                payment_method_id = transaction_in.payment_method_id,
                transaction_type = transaction_in.transaction_type,
                description = transaction_in.description,
                amount = transaction_in.amount,
            )
        db.add(transaction_item)
        db.commit()
        db.refresh(transaction_item)
        return transaction_item.id
        
    def update(self, db: Session, transaction_id: int, transaction_in: TransactionBase):
        transaction_item = self.get(db, transaction_id)
        
        transaction_item.payment_method_id = transaction_in.payment_method_id
        transaction_item.transaction_type = transaction_in.transaction_type
        transaction_item.description = transaction_in.description
        transaction_item.amount = transaction_in.amount
        transaction_item.status = transaction_in.status
        
        db.commit()
        db.refresh(transaction_item)
    
    def delete(self, db: Session, transaction_id: int):
        transaction_item = self.get(db, transaction_id)
        if transaction_item.order_id:
            raise HTTPException(status_code=400, detail="Can't delete this transaction!")
        db.delete(transaction_item)
        db.commit()
    
    def pay(self, db: Session, transaction_id: int, callback_url: str):
        
        transaction_item = self.get(db, transaction_id)
        pay_response: PayTransactionRes = payment_service.request_pay(transaction_item.amount, transaction_item.description, callback_url)
        
        transaction_item.portal_in = datetime.now()
        transaction_item.res_number = pay_response.res_number
        
        db.commit()
        db.refresh(transaction_item)
        
        return pay_response
    
    def verify(db: Session, res_number: str, status: str):
        transaction_item = db.query(Transaction).filter_by(res_number=res_number).first()
        
        verify_data = VerifyTransaction(
            status=status,
            res_number=res_number,
            amount=transaction_item.amount
        )
        verify_response: VerifyTransactionRes = payment_service.verify_pay(verify_data)
        
        transaction_item.status = verify_response.status
        transaction_item.portal_out = datetime.now()
        transaction_item.ref_id = verify_response.ref_id
        transaction_item.fee = verify_response.fee
        transaction_item.fee_type = verify_response.fee_type
        
        db.commit()
        db.refresh(transaction_item)
        
        return transaction_item
    
transaction_service = TransactionService()