
from datetime import datetime
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status
from db.models.product import Category
from schemas.pagination import Pagination
from schemas.category import CategoryCreate


class CategoryService:
    
    def get_all(self, db: Session, page: int, size: int):
        query = db.query(Category).order_by(Category.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get(self, db: Session, category_id: int):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="دسته بندی مورد نظر یافت نشد!")
        return category
    
    def create(self, db: Session, cat_in: CategoryCreate):
        category_item = db.query(Category).filter(Category.slug == cat_in.slug).first()
        if category_item:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='لینک ارسالی تکراری می باشد')
        db_category = Category(name=cat_in.name, slug=cat_in.slug, description=cat_in.description, parent_id=cat_in.parent_id)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    def update(self, db: Session, category_id: int, category_in: CategoryCreate):
        category_item = db.query(Category).filter(Category.id == category_id).first()
        if not category_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="دسته بندی مورد نظر یافت نشد!")
        category_item.name = category_in.name
        category_item.slug = category_in.slug
        category_item.description = category_in.description
        category_item.parent_id = category_in.parent_id
        category_item.updated_at = datetime.now()
        db.commit()
        db.refresh(category_item)
        return category_item
    
    def delete(self, db: Session, category_id: int):
        category_item = db.query(Category).filter(Category.id==category_id).first()
        if not category_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="دسته بندی مورد نظر یافت نشد!")
        db.delete(category_item)
        db.commit()
        return category_item


category_service = CategoryService()