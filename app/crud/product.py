from typing import List
from fastapi import HTTPException
from sqlalchemy import and_, text
from sqlalchemy.orm import Session, joinedload
from models import File, User, Category
from models.product import Attribute, Product, ProductAttribute, ProductType, ProductVariation, Status, VariationAttribute
from schemas.pagination import Pagination
from schemas.product import ProductConfig, ProductCreate, ProductUpdate
from starlette import status


class ProductService:
    
    def get_products(self, db: Session, page: int, size: int):
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
                min_variation = min(product.variations, key=lambda var: var.sales_price)
                product.var_id = min_variation.id
                product.sku = min_variation.sku
                product.unit_price = min_variation.unit_price
                product.sales_price = min_variation.sales_price
                product.quantity = min_variation.quantity
                product.reserved_quantity = min_variation.reserved_quantity
                product.var_status = min_variation.status
            
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get_home_products(self, db: Session, product_config: ProductConfig):
    
        query = db.query(
            Product,
            ProductVariation.id.label('var_id'),
            ProductVariation.unit_price,
            ProductVariation.sales_price, 
            ProductVariation.quantity, 
            ProductVariation.status.label('var_status')
            ).join(ProductVariation).options(
                joinedload(Product.categories).load_only(Category.id, Category.name,Category.slug, Category.parent_id),
                joinedload(Product.files)
            ).filter(Product.status == Status.PUBLISHED)
        
        # Apply filters
        if product_config.categories:
            query = query.filter(and_(*[Product.categories.any(Category.id == cat_id) for cat_id in product_config.categories]))
        
        if product_config.price_min is not None:
            query = query.filter(ProductVariation.sales_price >= product_config.price_min)
        
        if product_config.price_max is not None:
            query = query.filter(ProductVariation.sales_price <= product_config.price_max)
        
        # Order by
        if product_config.order_by == 'newest':
            query = query.order_by(Product.created_at.desc())
        elif product_config.order_by == 'expensive':
            query = query.order_by(ProductVariation.sales_price.desc())
        elif product_config.order_by == 'cheapest':
            query = query.order_by(ProductVariation.sales_price)
        
        # Paginate
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, product_config.paginate.page, product_config.paginate.size)
        items = paginated_query.all()
        
        # Convert each product to ProductList schema
        product_lists = [
            {
                'id': item.Product.id,
                'name': item.Product.name,
                'slug': item.Product.slug,
                'description': item.Product.description,
                'featured': item.Product.featured,
                'categories': item.Product.categories,
                'thumbnail': next((file for file in item.Product.files if file.is_thumbnail), None),
                'var_id': item.var_id,
                'unit_price': item.unit_price,
                'sales_price': item.sales_price,
                'quantity': item.quantity,
                'var_status': item.var_status,
            } for item in items
        ]
        
        pagination = Pagination(
            page=product_config.paginate.page,
            size=product_config.paginate.size,
            total_items=total_items,
            total_pages=total_pages
        )
        return product_lists, pagination
    
    def get(self, db: Session, product_slug: str):
        
        product_item = db.query(Product).options(
                joinedload(Product.user).load_only(User.id, User.username),
                joinedload(Product.files),
                joinedload(Product.categories).load_only(Category.id, Category.name, Category.slug, Category.parent_id),
                joinedload(Product.attributes).joinedload(ProductAttribute.attribute),
                joinedload(Product.variations)
                    .joinedload(ProductVariation.variation_attributes)
                    .joinedload(VariationAttribute.product_attribute)
                    .joinedload(ProductAttribute.attribute),
                joinedload(Product.tags)
                ).filter(Product.slug == product_slug).first()
        
        if not product_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='محصول مورد نظر پیدا نشد')
        
        # اضافه کردن لیست ویژگی‌ها به محصول
        product_item.attributes_list = [
            {'name': attr.attribute.name, 'value': attr.value} for attr in product_item.attributes
        ]
        
        # features list of variation
        for var in product_item.variations:
            var.attributes_list = [
                {
                    'name': va.product_attribute.attribute.name,
                    'value': va.product_attribute.value
                } for va in var.variation_attributes
            ]
        
        return product_item
    
    def get_by_id(self, db: Session, product_id: int):
        product_item = db.query(Product).filter(Product.id == product_id).first()
        
        if not product_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='محصول مورد نظر پیدا نشد')
        
        return product_item
    
    def create(self, db: Session, product_in: ProductCreate, current_user: str):
        product_item = db.query(Product).filter(Product.slug == product_in.slug).first()
        if product_item:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='لینک ارسالی تکراری می باشد')
        
        product_type = (
            ProductType.VARIABLE if product_in.variations and len(product_in.variations) > 1
            else ProductType.SIMPLE
        )
        
        product = Product(
            name=product_in.name,
            slug=product_in.slug,
            type=product_type,
            user_id=int(current_user),
            featured=product_in.featured,
            description=product_in.description,
            body=product_in.body,
            status=product_in.status,
        )
        db.add(product)
        db.flush()  # اختصاص id به product

        # Add categories
        if product_in.category_ids:
            product.categories = [db.query(Category).get(cat_id) for cat_id in product_in.category_ids]
            
        # Add images
        if product_in.files:
            for img in product_in.files:
                image = File(
                    url=img.url,
                    alt=img.alt,
                    is_thumbnail=img.is_thumbnail,
                    order=img.order,
                    type=img.type,
                    entity_type='product'
                )
                product.files.append(image)


        # دیکشنری نگهدارنده ویژگی‌های محصول: کلید (attribute_id, value) -> شیء ProductAttribute
        prod_attr_map = {}
        
        # Add attributes
        if product_in.attributes:
            for attr in product_in.attributes:
                product_attr = ProductAttribute(
                    attribute_id=attr.attribute_id,
                    value=attr.value,
                    show_top=attr.show_top
                )
                product.attributes.append(product_attr)
                db.flush()  # اختصاص id به product_attr
                prod_attr_map[(attr.attribute_id, attr.value)] = product_attr

        # Add variations
        if product_in.variations:
            for var in product_in.variations:
                # check sku variation
                variation = db.query(ProductVariation).filter(ProductVariation.sku == var.sku).first()
                if variation:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'متفیر با شناسه {var.sku} تکراری می باشد')
                variation = ProductVariation(
                    sku=var.sku,
                    cost_price=var.cost_price,
                    unit_price=var.unit_price,
                    sales_price=var.sales_price,
                    quantity=var.quantity,
                    low_stock_threshold=var.low_stock_threshold,
                    weight=var.weight,
                    status=var.status
                )
                
                # پردازش ویژگی‌های واریشن (هر کدام شامل attribute_id و value)
                for var_attr in var.variation_attributes:
                    key = (var_attr.attribute_id, var_attr.value)
                    # استفاده از ویژگی موجود
                    if key in prod_attr_map:
                        pa = prod_attr_map[key]
                    # ایجاد VariationAttribute با ارجاع به ProductAttribute
                    variation_attr = VariationAttribute(product_attribute_id=pa.id)
                    variation.variation_attributes.append(variation_attr)
                
                product.variations.append(variation)

        db.commit()
        db.refresh(product)
        return product
    
    def update(self, db: Session, product_slug: str, product_in: ProductUpdate, current_user: str):

        product_db = db.query(Product).filter(Product.slug == product_slug).first()
        if not product_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='محصول مورد نظر پیدا نشد')
        
        if product_in.slug != product_slug:
            existing_product_id = db.query(Product.id).filter(Product.slug == product_in.slug).scalar()
            if existing_product_id and existing_product_id != product_db.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='لینک ارسالی تکراری می باشد')
        
        product_db.name = product_in.name
        product_db.slug = product_in.slug
        product_db.type = ProductType.VARIABLE if len(product_in.variations) > 1 else ProductType.SIMPLE
        product_db.featured = product_in.featured
        product_db.description = product_in.description
        product_db.body = product_in.body
        product_db.status = product_in.status
        
        # Update categories
        if product_in.category_ids:
            product_db.categories = [db.query(Category).get(cat_id) for cat_id in product_in.category_ids]
        
        if product_in.deleted_image_ids:
                product_db.files = [image for image in product_db.files if image.id not in product_in.deleted_image_ids]
        
        for img in product_in.files:
            if hasattr(img, "id") and img.id:
                # Update existing images
                image_item = db.query(File).filter(File.id == img.id).first()
                if image_item:
                    image_item.url = img.url
                    image_item.alt = img.alt
                    image_item.order = img.order
                    image_item.type = img.type
                    image_item.is_thumbnail = img.is_thumbnail
            else:
                image = File(
                    url=img.url,
                    alt=img.alt,
                    is_thumbnail=img.is_thumbnail,
                    order=img.order,
                    type=img.type,
                    entity_type='product'
                )
                product_db.files.append(image)
        
        if product_in.deleted_attr_ids:
            product_db.attributes = [attr for attr in product_db.attributes if attr.id not in product_in.deleted_attr_ids]
        
        # attributes = {attr.id: attr for attr in product_db.attributes}
        for attr in product_in.attributes:
            if hasattr(attr, "id") and attr.id:
                # Update existing attribute
                product_attr = db.query(ProductAttribute).filter(ProductAttribute.id == attr.id).first()
                product_attr.value = attr.value
                product_attr.show_top = attr.show_top
                product_attr.attribute_id = attr.attribute_id
            else:
                product_attr = ProductAttribute(
                    attribute_id=attr.attribute_id,
                    value=attr.value,
                    show_top=attr.show_top
                )
                product_db.attributes.append(product_attr)
                db.flush()
        
        # ایجاد دیکشنری نگهدارنده ویژگی‌های محصول جهت استفاده در واریشن‌ها
        prod_attr_map = {}
        for pa in product_db.attributes:
            key = (pa.attribute_id, pa.value)
            prod_attr_map[key] = pa
            
        if product_in.deleted_var_ids:
                product_db.variations = [var for var in product_db.variations if var.id not in product_in.deleted_var_ids]

        for var in product_in.variations:
            
            if hasattr(var, "id") and var.id:
                # Retrieve and update the existing variation
                var_item = db.query(ProductVariation).filter(ProductVariation.id == var.id).first()
                # SKU is not updated as it's a unique identifier and should not change
                # var_item.sku = var.sku
                if var_item:
                    var_item.unit_price = var.unit_price
                    var_item.sales_price = var.sales_price
                    var_item.cost_price = var.cost_price
                    var_item.quantity = var.quantity
                    var_item.low_stock_threshold = var.low_stock_threshold
                    var_item.weight = var.weight
                    var_item.status = var.status
                    
                    # حذف واریشن اتربیوت‌های قدیمی و اضافه کردن مجدد بر اساس ورودی جدید
                    var_item.variation_attributes.clear()
                    # پردازش ویژگی‌های واریشن (هر کدام شامل attribute_id و value)
                    for var_attr in var.variation_attributes:
                        key = (var_attr.attribute_id, var_attr.value)
                        # استفاده از ویژگی موجود
                        if key in prod_attr_map:
                            pa = prod_attr_map[key]
                            # ایجاد VariationAttribute با ارجاع به ProductAttribute
                            variation_attr = VariationAttribute(product_attribute_id=pa.id)
                            var_item.variation_attributes.append(variation_attr)
                            variation_attr.product_variation_id = var_item.id
                
            else:
                # check sku variation
                exsiting_variation = db.query(ProductVariation).filter(ProductVariation.sku == var.sku).first()
                if exsiting_variation:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'متفیر با شناسه {var.sku} تکراری می باشد')
                
                variable = ProductVariation(
                    sku = var.sku,
                    unit_price = var.unit_price,
                    sales_price = var.sales_price,
                    cost_price = var.cost_price,
                    quantity = var.quantity,
                    low_stock_threshold = var.low_stock_threshold,
                    weight = var.weight,
                    status = var.status
                )
                db.add(variable)
                db.flush()
                for var_attr in var.variation_attributes:
                    key = (var_attr.attribute_id, var_attr.value)
                    # استفاده از ویژگی موجود
                    if key in prod_attr_map:
                        pa = prod_attr_map[key]
                        # ایجاد VariationAttribute با ارجاع به ProductAttribute
                        variation_attr = VariationAttribute(product_attribute_id=pa.id)
                        variable.variation_attributes.append(variation_attr)
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
    
    def get_variation_by_id(self, db: Session, variation_id: int):
        variation_item = db.query(ProductVariation).filter(ProductVariation.id == variation_id).first()
        if not variation_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='متغیر پیدا نشد')
        return variation_item
    
    def get_variations_by_ids(self, db: Session, variation_ids: List[int]):
        return db.query(ProductVariation).filter(ProductVariation.id.in_(variation_ids)).all()
    
    def get_variation_total_price(self, db: Session, variation_id: int, quantity: int) -> float:
        if not variation_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='شناسه متغیر اجباری می باشد')
        
        variation = self.get_variation_by_id(db, variation_id)
        
        return float(variation.sales_price * quantity)
            
    def reserve_quantity(self, db: Session, variation_id: int, quantity: int):
        # Atomic query
        try:
            db.execute(
                text("UPDATE product_variations "
                       "SET quantity = quantity - :quantity, reserved_quantity = reserved_quantity + :quantity "
                       "WHERE id = :variation_id AND quantity >= :quantity"),
                       {"quantity": quantity, "variation_id": variation_id}
                )
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'عملیات رزرو تعداد محصول با خطا مواجه شد')
    
    def get_attributes(self, db: Session):
        attributes = db.query(Attribute).all()
        return attributes
    
    def create_attribute(self, db: Session, attribute_name: str):
        attribute = Attribute(name=attribute_name)
        db.add(attribute)
        db.commit()
        db.refresh(attribute)
        return attribute

product_service = ProductService()