import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.setting import Setting
from schemas.setting import SettingBase, SettingItem

class SettingService:
    
    def get_all(self, db: Session):
        settings = db.query(Setting).all()
        for setting in settings:
            if isinstance(setting.value, str):
                setting.value = json.loads(setting.value)
        return settings
    
    def get(self, db: Session, setting_id: int):
        setting = db.query(Setting).filter_by(id=setting_id).first()
        if not setting:
            raise HTTPException(status_code=404, detail='setting item not found!')
        if isinstance(setting.value, str):
                setting.value = json.loads(setting.value)
        return setting
    
    def create(self, db: Session, data: SettingBase):
        new_setting = Setting(
            key=data.key,
            value=json.dumps(data.value),
            description=data.description,
            is_active=True
        )
        db.add(new_setting)
        db.commit()
        db.refresh(new_setting)
        return new_setting
    
    def update(self, db: Session, data: SettingItem, setting_id: int):
        setting = db.query(Setting).filter_by(id=setting_id).first()
        if not setting:
            raise HTTPException(status_code=404, detail='setting item not found!')
        setting.key = data.key
        setting.value = json.dumps(data.value)
        setting.description = data.description
        setting.is_active = data.is_active
        db.commit()
        db.refresh(setting)
        return setting
    
    def delete(self, db: Session, setting_id: int):
        setting = db.query(Setting).filter_by(id=setting_id).first()
        if not setting:
            raise HTTPException(status_code=404, detail='setting item not found!')
        
        db.delete(setting)
        db.commit()
    
setting_service = SettingService()