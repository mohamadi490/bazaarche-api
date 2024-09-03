from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.file import File
from models.product import Product, ProductAttribute, ProductVariation
from models.collections import Category
from sqlalchemy.orm import joinedload
from models.user import User
from schemas.pagination import Pagination
from schemas.product import ProductCreate, ProductUpdate
from starlette import status


class ProductService:
    
    def get_all(self, db: Session, page: int, size: int):
        query = db.query(Product).options(
            joinedload(Product.user).load_only(User.id, User.username),
            joinedload(Product.files),
            joinedload(Product.variations),
            joinedload(Product.categories).load_only(Category.id, Category.name,Category.slug, Category.parent_id),
            ).order_by(Product.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        for product in items:
            product.categories = [cat for cat in product.categories if cat.parent_id is None]
            if product.variations:
                min_variation = min(product.variations, key=lambda var: var.final_price)
                product.var_id = min_variation.id
                product.sku = min_variation.sku
                product.price = min_variation.price
                product.final_price = min_variation.final_price
                product.quantity = min_variation.quantity
                product.var_status = min_variation.status
            
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
        
    
    def get(self, db: Session, product_slug: str):
        product_item = db.query(Product).options(
                joinedload(Product.user).load_only(User.id, User.username),
                joinedload(Product.files),
                joinedload(Product.categories).load_only(Category.id, Category.name,Category.slug, Category.parent_id),
                joinedload(Product.attributes).joinedload(ProductAttribute.attribute),
                joinedload(Product.variations),
                joinedload(Product.tags)).filter(Product.slug == product_slug).first()
        
        if not product_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='محصول مورد نظر پیدا نشد')
        
        return product_item
    
    
    def create(self, db: Session, product_in: ProductCreate, current_user: str):
        product_item = db.query(Product).filter(Product.slug == product_in.slug).first()
        if product_item:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='لینک ارسالی تکراری می باشد')
        
        product = Product(
            name=product_in.name,
            slug=product_in.slug,
            type=product_in.type,
            user_id=int(current_user),
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
                image = File(
                    url=img.url,
                    alt=img.alt,
                    is_thumbnail=img.is_thumbnail,
                    order=img.order,
                    entity_type='product'
                )
                product.files.append(image)

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
    
    def update(self, db: Session, product_slug: str, product_in: ProductUpdate, current_user: str):

        product_db = db.query(Product).filter(Product.slug == product_slug).first()
        if not product_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='محصول مورد نظر پیدا نشد')
        
        product_db.name = product_in.name
        product_db.slug = product_in.slug
        product_db.type = product_in.type
        product_db.featured = product_in.featured
        product_db.description = product_in.description
        product_db.body = product_in.body
        product_db.status = product_in.status
        
        # Update categories
        if product_in.category_ids:
            product_db.categories = [db.query(Category).get(cat_id) for cat_id in product_in.category_ids]
        
        if product_in.deleted_attr_ids:
                product_db.attributes = [attr for attr in product_db.attributes if attr.id not in product_in.deleted_attr_ids]
        
        attributes = {attr.id: attr for attr in product_db.attributes}
        for attr in product_in.attributes:
            if attr.id in attributes:
                # Update existing attribute
                item = db.query(ProductAttribute).filter(ProductAttribute.id == attr.id).first()
                item.value = attr.value
                item.show_top = attr.show_top
                item.attribute_id = attr.attribute_id
            else:
                product_attr = ProductAttribute(
                    attribute_id=attr.attribute_id,
                    value=attr.value,
                    show_top=attr.show_top
                )
                product_db.attributes.append(product_attr)
        
        if product_in.deleted_image_ids:
                product_db.files = [image for image in product_db.files if image.id not in product_in.deleted_image_ids]
        
        images = {img.id: img for img in product_db.files}
        for img in product_in.images:
            if img.id in images:
                # Update existing images
                image_item = db.query(File).filter(File.id == img.id).first()
                image_item.url = img.url
                image_item.alt = img.alt
                image_item.order = img.order
                image_item.is_thumbnail = img.is_thumbnail
            else:
                image = File(
                    url=img.url,
                    alt=img.alt,
                    is_thumbnail=img.is_thumbnail,
                    order=img.order,
                    entity_type='product'
                )
                product_db.files.append(image)
            
        if product_in.deleted_var_ids:
                product_db.variations = [var for var in product_db.variations if var.id not in product_in.deleted_var_ids]

        variations = {var.id: var for var in product_db.variations}
        for var in product_in.variations:
            if var.id in variations:
                # Update existing variation
                var_item = db.query(ProductVariation).filter(ProductVariation.id == var.id).first()
                var_item.sku = var.sku
                var_item.price = var.price
                var_item.final_price = var.final_price
                var_item.cost_price = var.cost_price
                var_item.quantity = var.quantity
                var_item.low_stock_threshold = var.low_stock_threshold
                var_item.status = var.status
            else:
                variable = ProductVariation(
                    sku = var.sku,
                    price = var.price,
                    final_price = var.final_price,
                    cost_price = var.cost_price,
                    quantity = var.quantity,
                    low_stock_threshold = var.low_stock_threshold,
                    status = var.status
                )
                product_db.variations.append(variable)
                
                
        db.commit()
        db.refresh(product_db)
        return product_db
    
    def delete(self, db: Session, product_slug: str, current_user: str):
        product_db = db.query(Product).filter(Product.slug == product_slug).first()
        
        if not product_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='محصول مورد نظر یافت نشد')
        
        db.delete(product_db)
        db.commit()

product_service = ProductService()