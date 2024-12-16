from operator import or_
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from models.shipping import ShippingMethod, ShippingArea
from models.address import Province, City
from schemas.shipping import ShippingMethodData, ShippingAreaItem
from schemas.pagination import Pagination
from sqlalchemy.sql import exists

class ShippingMethods:
    def get_all(self, db: Session, page: int, size: int):
        query = db.query(ShippingMethod).order_by(ShippingMethod.created_at.desc())
        paginated_query, total_items, total_pages = Pagination.paginate_query(query, page, size)
        items = paginated_query.all()
        pagination = Pagination(page=page, size=size, total_items=total_items, total_pages=total_pages)
        return items, pagination
    
    def get(self, db: Session, shipping_id: int):
        shipping_item = db.query(ShippingMethod).options(joinedload(ShippingMethod.shipping_areas)).filter_by(id=shipping_id).first()
        if not shipping_item:
            raise HTTPException(status_code=404, detail="shipping method not found!")
        
        # Grouping cities by province ID and price_modifier
        areas = {}
        for area in shipping_item.shipping_areas:
            key = (area.province_id, area.price_modifier)
            if key not in areas:
                areas[key] = {"id": area.province_id, "city_ids": [], "price": area.price_modifier}
            if area.city_id is not None:
                areas[key]["city_ids"].append(area.city_id)
                
        # Updating the shipping_item's areas with the grouped cities
        shipping_item.areas = list(areas.values())
        
        return shipping_item
    
    def add_areas(self, db:Session, areas: List[ShippingAreaItem], shipping_id: int):
        shipping_areas = []
        if not areas:
            raise HTTPException(status_code=400, detail="No provinces provided.")
        province_exists = db.query(exists().where(Province.id.in_(area.id for area in areas))).scalar()
        if not province_exists:
            raise HTTPException(status_code=400, detail="One or more province IDs are invalid.")
        for area in areas:
            if area.city_ids:  # Check if city_ids is not empty
                city_exists = db.query(exists().where(City.id.in_(area.city_ids))).scalar()
                if not city_exists:
                    raise HTTPException(status_code=400, detail="One or more city IDs are invalid.")
                for id in area.city_ids:
                    shipping_areas.append(
                        ShippingArea(
                            shipping_method_id=shipping_id,
                            province_id=area.id,
                            city_id=id,
                            price_modifier=area.price,
                        )
                    )
            else:  # If city_ids is empty, append only province_id
                shipping_areas.append(
                    ShippingArea(
                        shipping_method_id=shipping_id,
                        province_id=area.id,
                        price_modifier=area.price,
                    )
                )
        
        return shipping_areas
        
    def create(self, db: Session, data:ShippingMethodData):
        # try:
            shipping_method = ShippingMethod(name= data.name,
                                             description=data.description,
                                             estimated_days=data.estimated_days, 
                                             is_active=data.is_active)
            db.add(shipping_method)
            db.commit()
            db.refresh(shipping_method)
            
            
            areas = self.add_areas(db, data.areas, shipping_method.id)
            
            db.add_all(areas)
            db.commit()

            # Refresh and return the shipping method with areas
            db.refresh(shipping_method)
            shipping_method.shipping_areas = areas  # Add the areas to the shipping method for response
            return shipping_method
            
        # except Exception as e:
        #     db.rollback()
        #     raise HTTPException(status_code=500, detail='failed to create shipping method!')
        
    def update(self, db: Session, method_id: int, data: ShippingMethodData):
        shipping_method = db.query(ShippingMethod).filter(ShippingMethod.id == method_id).first()
        if not shipping_method:
            raise HTTPException(status_code=404, detail="shipping method not found!")
        
        shipping_method.name = data.name
        shipping_method.description = data.description
        shipping_method.estimated_days = data.estimated_days
        shipping_method.is_active = data.is_active
        
        db.commit()
        db.refresh(shipping_method)
        
        # Remove all existing areas for the shipping method
        db.query(ShippingArea).filter(ShippingArea.shipping_method_id == method_id).delete(synchronize_session=False)
        db.commit()
        
        areas = self.add_areas(db, data.areas, method_id)
    
        # Add all areas to the session
        db.add_all(areas)
        db.commit()
    
        # Refresh and return the shipping method with areas
        db.refresh(shipping_method)
        shipping_method.shipping_areas = areas  # Add the areas to the shipping method for response
        return shipping_method
    
    def delete(self, db: Session, method_id: int):
        shipping_method = db.query(ShippingMethod).filter(ShippingMethod.id == method_id).first()
        if not shipping_method:
            raise HTTPException(status_code=404, detail="shipping method not found!")
        
        # Delete associated shipping areas
        db.query(ShippingArea).filter(ShippingArea.shipping_method_id == method_id).delete(synchronize_session=False)
        db.commit()
        
        # delete the shipping method
        db.delete(shipping_method)
        db.commit()
        
    def delete_all(self, db: Session):
        db.query(ShippingArea).delete(synchronize_session=False)
        db.commit()
        db.query(ShippingMethod).delete(synchronize_session=False)
        db.commit()
    
    def get_methods(self, db: Session, province_id: int, city_id: int):
        query = db.query(
            ShippingMethod.id,
            ShippingMethod.name,
            ShippingMethod.description,
            ShippingMethod.estimated_days,
            ShippingMethod.is_active,
            ShippingArea.price_modifier
        ).join(
            ShippingArea, ShippingMethod.id == ShippingArea.shipping_method_id
        ).filter(
            ShippingMethod.is_active == True,
            ShippingArea.province_id == province_id
        )

        if city_id:
            query = query.filter(
                or_(ShippingArea.city_id == city_id, ShippingArea.city_id == None)
            )

        shipping_methods_list = [
            {
                "id": method.id,
                "name": method.name,
                "description": method.description,
                "estimated_days": method.estimated_days,
                "is_active": method.is_active,
                "price": method.price_modifier,
            }
            for method in query
        ]

        if not shipping_methods_list:
            if not db.query(exists().where(ShippingArea.province_id == province_id)).scalar():
                raise HTTPException(status_code=404, detail="The provided province does not exist.")
            if city_id and not db.query(exists().where(ShippingArea.province_id == province_id, ShippingArea.city_id == city_id)).scalar():
                raise HTTPException(status_code=404, detail="The provided city does not exist.")

        return sorted(shipping_methods_list, key=lambda x: x['price'])

shipping_service = ShippingMethods()