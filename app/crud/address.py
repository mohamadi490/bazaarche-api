# services/address_service.py
from fastapi import HTTPException
from sqlalchemy import exists
from sqlalchemy.orm import Session
from models import Address
from models.address import City, Province
from schemas.address import UserAddressBase, UserAddressCreate

class AddressService:
    
    @staticmethod
    def get_user_adresses(db: Session, user_id: int):
        return db.query(Address
        ).join(City, Address.city_id == City.id) \
        .join(Province, Address.province_id == Province.id) \
        .filter(Address.user_id == user_id).order_by(Address.created_at.desc()).all()

    @staticmethod
    def get_address(db: Session, address_id: int, current_user: str):
        return db.query(Address).filter(Address.user_id == int(current_user)).filter(Address.id == address_id).first()

    @staticmethod
    def create_address(db: Session, address_in: UserAddressCreate, current_user: str):
        province_exists = db.query(exists().where(Province.id == address_in.province_id)).scalar()
        city_exists = db.query(exists().where(City.id == address_in.city_id)).scalar()
        if not province_exists or not city_exists:
            raise HTTPException(status_code=400, detail="شناسه شهر یا استان اشتباه است!")
        db_address = Address(
            user_id = int(current_user),
            city_id = address_in.city_id,
            province_id = address_in.province_id,
            country_id = 1,
            title = address_in.title,
            postal_code = address_in.postal_code,
            phone_number = address_in.phone_number,
            line_1 = address_in.line_1,
            line_2 = address_in.line_2
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address
    
    @staticmethod
    def update_address(db: Session, address_id: int, address_in: UserAddressBase, current_user: str):
        db_address = db.query(Address).filter(Address.id == address_id).filter(Address.user_id == int(current_user)).first()
        if db_address:
            for key, value in address_in.dict(exclude_unset=True).items():
                setattr(db_address, key, value)
            db.commit()
            db.refresh(db_address)
        return db_address
    
    @staticmethod
    def delete_address(db: Session, address_id: int, current_user: str):
        db_address = db.query(Address).filter(Address.user_id == int(current_user)).filter(Address.id == address_id).first()
        if db_address:
            db.delete(db_address)
            db.commit()
        return db_address
    
    def get_provinces(self, db: Session):
        return db.query(Province).all()
    
    def get_cities(self, db: Session, province_id: int):
        return db.query(City).filter(City.province_id == province_id).all()

address_service = AddressService()