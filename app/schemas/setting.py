from typing import Any, Dict
from pydantic import BaseModel

class SettingBase(BaseModel):
    key: str
    value: Dict[str, Any] | str
    description: str

class SettingItem(SettingBase):
    is_active: bool