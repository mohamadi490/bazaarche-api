from typing import List
from fastapi import HTTPException
from sqlalchemy import and_, or_, text, func
from sqlalchemy.orm import Session, joinedload
from models import File, User, Category
from models.product import Attribute, Product, ProductAttribute, ProductType, ProductVariation, Status, VariationAttribute
from schemas.pagination import Pagination
from schemas.product import ProductConfig, ProductCreate, ProductUpdate, AdminProductsRequest
from starlette import status


class ProductService:
    
    def get_admin_products(self, db: Session, product_request: AdminProductsRequest):
        """
        واکشی محصولات جهت بخش ادمین با امکان جستجو، فیلترینگ و ordering داینامیک.

        پارامترها:
          - search_params: دیکشنری شامل کلیدهای فیلترینگ (مثلاً 'name', 'sku', 'created_from', 'created_to', …)
          - order_by: نام ستونی که باید مرتب شود (مثلاً 'name', 'created_at', 'sales_price')
          - order_dir: جهت مرتب‌سازی ('asc' یا 'desc')
        """

        # کوئری اولیه با joinedload روابط مورد نیاز
        query = db.query(Product).options(
            joinedload(Product.user).load_only(User.id, User.username),
            joinedload(Product.files),
            joinedload(Product.variations),
            joinedload(Product.categories).load_only(Category.id, Category.name, Category.slug, Category.parent_id)
        )
    
        # فیلترهای پیش‌فرض: نمایش محصولات منتشر شده
        query = query.filter(Product.status == Status.PUBLISHED)
    
        # اعمال فیلترهای داینامیک از search_params
        if product_request.search_params:
            if product_request.search_params.name:
                query = query.filter(Product.name.ilike(f"%{product_request.search_params.name}%"))
            if product_request.search_params.sku:
                query = query.join(Product.variations).filter(ProductVariation.sku.ilike(f"%{product_request.search_params.sku}%"))
            if product_request.search_params.created_from:
                query = query.filter(Product.created_at >= product_request.search_params.created_from)
            if product_request.search_params.created_to:
                query = query.filter(Product.created_at <= product_request.search_params.created_to)
    
        # تعیین ordering داینامیک
        # نگاشت ستون‌های قابل مرتب‌سازی به فیلدهای واقعی در مدل
        order_map = {
            "name": Product.name,
            "created_at": Product.created_at,
            "updated_at": Product.updated_at,
            "sales_price": None
        }
        if product_request.order_by:
            if product_request.order_by == "sales_price":
                # زیرکوئری جهت بدست آوردن کمترین sales_price برای هر محصول
                min_price_subq = (
                    db.query(
                        ProductVariation.product_id,
                        func.min(ProductVariation.sales_price).label("min_sales_price")
                    )
                    .group_by(ProductVariation.product_id)
                    .subquery()
                )
                query = query.join(min_price_subq, Product.id == min_price_subq.c.product_id)
                col = min_price_subq.c.min_sales_price
            else:
                col = order_map.get(product_request.order_by)
            
            if col is not None:
                if product_request.order_dir.lower() == "desc":
                    query = query.order_by(col.desc())
                else:
                    query = query.order_by(col)
            else:
                query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.created_at.desc())
    
        # صفحه‌بندی
        paginate_config = product_request.paginate
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, paginate_config.page, paginate_config.size)
        items = paginated_query.all()
    
        # پردازش نهایی هر محصول: انتخاب variation با کمترین sales_price به صورت پایتون
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
    
        pagination = Pagination(page=paginate_config.page, size=paginate_config.size, total_items=total_items, total_pages=total_pages)
        return items, pagination

    def get_home_products(self, db: Session, product_config: ProductConfig):
        # تعریف alias ها
        PV = ProductVariation
        P = Product

        # زیرکوئری: انتخاب variationها همراه با شماره ردیف (row_number) بر اساس sales_price (صعودی)
        # شرط: یا وضعیت variation برابر INSTOCK باشد یا محصول SIMPLE باشد
        variation_subq = (
            db.query(
                PV.id.label("var_id"),
                PV.sku,
                PV.product_id,
                PV.unit_price,
                PV.sales_price,
                PV.quantity,
                PV.status.label("var_status"),
                func.row_number().over(
                    partition_by=PV.product_id,
                    order_by=PV.sales_price
                ).label("rn")
            )
            .join(P, P.id == PV.product_id)
            .filter(
                or_(
                    PV.status == "INSTOCK",
                    P.type == ProductType.SIMPLE
                )
            )
            .subquery()
        )

        # کوئری اصلی: اتصال محصولات به زیرکوئری و انتخاب تنها ردیف‌هایی که rn == 1 دارند
        query = (
            db.query(
                P,
                variation_subq.c.var_id,
                variation_subq.c.sku,
                variation_subq.c.unit_price,
                variation_subq.c.sales_price,
                variation_subq.c.quantity,
                variation_subq.c.var_status
            )
            .select_from(P)
            .join(variation_subq, variation_subq.c.product_id == P.id)
            .filter(variation_subq.c.rn == 1)
            .options(
                joinedload(P.categories).load_only(Category.id, Category.name, Category.slug, Category.parent_id),
                joinedload(P.files)
            )
            .filter(P.status == Status.PUBLISHED)
        )
        
        # **اعمال فیلتر جستجو بر اساس نام محصول**
        if getattr(product_config, "keyword", None):
            # استفاده از ilike برای جستجو به صورت case-insensitive
            query = query.filter(P.name.icontains(f"%{product_config.keyword}%"))

        # اعمال فیلتر بر اساس دسته‌بندی‌ها
        if product_config.categories:
            query = query.filter(
                and_(*[P.categories.any(Category.id == cat_id) for cat_id in product_config.categories])
            )

        # اعمال فیلتر قیمت (استفاده از sales_price variation انتخاب شده)
        if product_config.price_min is not None:
            query = query.filter(variation_subq.c.sales_price >= product_config.price_min)
        if product_config.price_max is not None:
            query = query.filter(variation_subq.c.sales_price <= product_config.price_max)

        # مرتب‌سازی
        if product_config.order_by == 'newest':
            query = query.order_by(P.created_at.desc())
        elif product_config.order_by == 'expensive':
            query = query.order_by(variation_subq.c.sales_price.desc())
        elif product_config.order_by == 'cheapest':
            query = query.order_by(variation_subq.c.sales_price)

        # صفحه‌بندی
        paginated_query, total_items, total_pages = Pagination.paginate_query(
            query, product_config.paginate.page, product_config.paginate.size
        )
        items = paginated_query.all()

        # تبدیل نتایج به ساختار نهایی: اطلاعات محصول به همراه فیلدهای variation به صورت مسطح
        product_lists = []
        for product, var_id, sku, unit_price, sales_price, quantity, var_status in items:
            product_lists.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'description': product.description,
                'featured': product.featured,
                'categories': product.categories,
                'thumbnail': next((file for file in product.files if file.is_thumbnail), None),
                'var_id': var_id,
                'sku': sku,
                'unit_price': unit_price,
                'sales_price': sales_price,
                'quantity': quantity,
                'var_status': var_status,
            })
        
        filters_data = self.get_products_filtering(db)

        pagination = Pagination(
            page=product_config.paginate.page,
            size=product_config.paginate.size,
            total_items=total_items,
            total_pages=total_pages
        )

        result = {
            "products": product_lists,
            "filters": filters_data,
        }

        return result , pagination

    def get_info(self, db: Session, product_slug: str):
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

    def get_products_filtering(self, db: Session):
        
        PV = ProductVariation
        P = Product
        
        # 1. محدوده قیمت: حداقل و حداکثر sales_price در میان variationهای فیلتر شده
        price_range_query = (
            db.query(
                func.min(PV.sales_price),
                func.max(PV.sales_price)
            )
            .join(P, P.id == PV.product_id)
            .filter(P.status == Status.PUBLISHED)
            .filter(
                or_(
                    PV.status == "INSTOCK",
                    P.type == ProductType.SIMPLE
                )
            )
        )
        # if product_config.categories:
        #     price_range_query = price_range_query.filter(
        #         and_(*[P.categories.any(Category.id == cat_id) for cat_id in product_config.categories])
        #     )
        min_price, max_price = price_range_query.first() or (0,0)

        # 2. دسته‌بندی‌های موجود (برای محصولات فیلتر شده)
        categories_query = (
            db.query(Category)
            .join(P.categories)
            .filter(P.status == Status.PUBLISHED)
        )
        available_categories = categories_query.distinct().all()

        # 3. گزینه‌های مرتب‌سازی (ثابت)
        ordering_options = ["newest", "expensive", "cheapest"]

        filters_data = {
            "min_price": min_price,
            "max_price": max_price,
            "categories": available_categories,
            "ordering_options": ordering_options,
        }
        
        return filters_data

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
    
    def finalize_reserved_quantity(self, db: Session, variation_id: int, quantity: int):
        try:
            product_variation = self.get_variation_by_id(db, variation_id)
            product_variation.reserved_quantity -= quantity
            db.add(product_variation)
            db.commit()
            db.refresh(product_variation)
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