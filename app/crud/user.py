from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import hash_password


class UserService:
    def get_all(self, db: Session):
        return db.query(User).all()
    
    def get(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()
    
    def get_by_phone_number(self, db: Session, phone_number: str):
        return db.query(User).filter(User.phone_number == phone_number).first()

    def create(self, db: Session, user_in: UserCreate):
        db_user = User(
        email = user_in.email,
        username = user_in.username,
        first_name = user_in.first_name,
        last_name = user_in.last_name,
        phone_number = user_in.phone_number,
        role_id = user_in.role_id,
        password = hash_password(user_in.password),
        is_active = True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    def create_quick(self, db: Session, username: str):
        db_user = User(phone_number=username, role_id=3, is_active=True)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, db_user: User, user_in: UserUpdate):
        if user_in.password:
            db_user.password = hash_password(user_in.password)
        db_user.is_active = user_in.is_active
        db.commit()
        db.refresh(db_user)

    def remove(self, db: Session, user_id: int):
        db_user = self.get(db, user_id)
        db.delete(db_user)
        db.commit()


user_service = UserService()