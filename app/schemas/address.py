from pydantic import BaseModel, Field, conint

class City(BaseModel):
    id: int
    name: str
    tag: str

class Province(BaseModel):
    id: int
    name: str
    tag: str

class UserAddressCreate(BaseModel):
    city_id: int = Field(gt=0, description="The city_id must be greater than zero")
    province_id: int = Field(gt=0, description="The province_id must be greater than zero")
    title: str = Field(min_length=3, description="اجباری است")
    postal_code: str = Field(max_length=10)
    phone_number: str = Field(max_length=11)
    line_1: str
    line_2: str

class UserAddressBase(BaseModel):
    city: City
    province: Province
    title: str
    postal_code: str
    phone_number: str
    line_1: str
    line_2: str

class UserAddress(UserAddressBase):
    id: int
    
    class Config:
        orm_mode = True
