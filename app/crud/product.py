from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models.image import Image
from db.models.product import Category, Product, ProductAttribute, ProductVariation
from sqlalchemy.orm import joinedload, contains_eager
from db.models.user import User
from schemas.pagination import Pagination
from schemas.product import ProductCreate
from starlette import status
import json


class ProductService:
    
    def get_all(self, db: Session, page: int, size: int):
        query = db.query(Product).options(
            joinedload(Product.user).load_only(User.id, User.username),
            joinedload(Product.images),
            joinedload(Product.variations),
            joinedload(Product.categories).load_only(Category.id, Category.name,Category.slug, Category.parent_id),
            ).order_by(Product.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        for product in items:
            product.categories = [cat for cat in product.categories if cat.parent_id is None]
            if product.variations:
                min_variation = min(product.variations, key=lambda var: var.final_price)
                product.sku = min_variation.sku
                product.price = min_variation.price
                product.final_price = min_variation.final_price
                product.quantity = min_variation.quantity
                product.var_status = min_variation.status
            
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
        
    
    def get(self, db: Session, product_slug: str):
        product_item = db.query(Product).options(
                joinedload(Product.images),
                joinedload(Product.categories),
                joinedload(Product.attributes).joinedload(ProductAttribute.attribute),
                joinedload(Product.variations),
                joinedload(Product.tags)).filter(Product.slug == product_slug).first()

        return product_item
    
    def create(self, db: Session, product_in: ProductCreate):
        product_item = db.query(Product).filter(Category.slug == product_in.slug).first()
        if product_item:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='لینک ارسالی تکراری می باشد')
        
        product = Product(
            name=product_in.name,
            slug=product_in.slug,
            type=product_in.type,
            user_id=1,
            featured=product_in.featured,
            description=product_in.description,
            body=product_in.body,
            status=product_in.status,
        )

        # Add categories
        if product_in.category_ids:
            product.categories = [db.query(Category).get(cat_id) for cat_id in product_in.category_ids]

        # Add attributes
        if product_in.attributes:
            for attr in product_in.attributes:
                product_attr = ProductAttribute(
                    attribute_id=attr.attribute_id,
                    value=attr.value,
                    show_top=attr.show_top
                )
                product.attributes.append(product_attr)

        # Add images
        if product_in.images:
            for img in product_in.images:
                image = Image(
                    url=img.url,
                    alt=img.alt,
                    is_thumbnail=img.is_thumbnail,
                    order=img.order
                )
                product.images.append(image)

        # Add variations
        if product_in.variations:
            for var in product_in.variations:
                variation = ProductVariation(
                    sku=var.sku,
                    cost_price=var.cost_price,
                    price=var.price,
                    final_price=var.final_price,
                    quantity=var.quantity,
                    low_stock_threshold=var.low_stock_threshold,
                    status=var.status
                )
                product.variations.append(variation)

        db.add(product)
        db.commit()
        db.refresh(product)
        return product


product_service = ProductService()