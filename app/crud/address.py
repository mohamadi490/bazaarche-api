# services/address_service.py
from sqlalchemy.orm import Session
from models import Address
from models.address import City, Country
from schemas.address import UserAddressBase, UserAddressCreate

class AddressService:
    @staticmethod
    def create_address(db: Session, address_in: UserAddressCreate, current_user: str):
        db_address = Address(
            user_id= int(current_user),
            city_id= address_in.city_id,
            country_id= address_in.country_id,
            postal_code= address_in.postal_code,
            phone_number= address_in.phone_number,
            line_1= address_in.line_1,
            line_2 = address_in.line_2
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address

    @staticmethod
    def get_address(db: Session, address_id: int, current_user: str):
        return db.query(Address).filter(Address.user_id == int(current_user)).filter(Address.id == address_id).first()
    
    @staticmethod
    def get_user_adresses(db: Session, user_id: int):
        return db.query(Address
        ).join(City, Address.city_id == City.id) \
        .join(Country, Address.country_id == Country.id) \
        .filter(Address.user_id == user_id).all()

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

address_service = AddressService()