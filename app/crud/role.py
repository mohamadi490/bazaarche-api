from datetime import datetime
from sqlalchemy.orm import Session
from schemas.pagination import Pagination
from models.user import Permission, Role
from schemas.role import RoleBase
from fastapi import HTTPException
from sqlalchemy.orm import joinedload

class RoleService:
    def get_all_query(self, db: Session, page: int, size: int):
        query = db.query(Role).options(joinedload(Role.permissions)).order_by(Role.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get(self, db: Session, role_id: int):
        return db.query(Role).filter(Role.id == role_id).first()
    
    def get_permissions(self, db: Session):
        permissions = db.query(Permission).all()
        return [item.name for item in permissions]
    
    def create(self, db: Session, role_in: RoleBase):
        permissions = db.query(Permission).filter(Permission.id.in_(role_in.permissions)).all()
        db_role = Role(name=role_in.name, tag=role_in.tag, permissions=permissions)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def update(self, db: Session, role_id: int, role_in: RoleBase):
        db_role = self.get(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="مقام مورد نظر یافت نشد!")
        permissions = db.query(Permission).filter(Permission.id.in_(role_in.permissions)).all()
        db_role.name = role_in.name
        db_role.tag = role_in.tag
        db_role.permissions = permissions
        db_role.updated_at = datetime.now()
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def delete(self, db: Session, role_id: int):
        db_role = self.get(db, role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="مقام مورد نظر یافت نشد!")
        db.delete(db_role)
        db.commit()
        return db_role
    
role_service = RoleService()