from pydantic import BaseModel

class PermissionBase(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    tag: str
    permissions: list[PermissionBase] | None = None
    
    class Config:
        from_attributes = True