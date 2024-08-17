from datetime import datetime
from db.models.verification_code import VerificationCode as vc_model
from sqlalchemy.orm import Session


class VerificationCodeService:
    
    def create_verification_code(self, db: Session, phone_number: str):
        return vc_model.create_code(db, phone_number)
    
    def get_valid_code(self, db: Session, phone_number:str, code: str):
        return db.query(vc_model).filter(vc_model.phone_number == phone_number, vc_model.code == code, vc_model.expires_at > datetime.now()).first()
    
    def mark_code_as_used(self, db: Session, code_id: int):
        verification_code = db.query(vc_model).filter(vc_model.id == code_id).first()
        if verification_code:
            verification_code.is_used = True
            db.commit()
            db.refresh(verification_code)

verification_code_service = VerificationCodeService()

    