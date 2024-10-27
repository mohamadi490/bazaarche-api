from pydantic import BaseModel

class City(BaseModel):
    id: int
    name: str
    tag: str

class Country(BaseModel):
    id: int
    name: str
    tag: str

class UserAddressCreate(BaseModel):
    city_id: int
    country_id: int
    postal_code: str
    phone_number: str
    line_1: str
    line_2: str

class UserAddressBase(BaseModel):
    city: City
    country: Country
    postal_code: str
    phone_number: str
    line_1: str
    line_2: str

class UserAddress(UserAddressBase):
    id: int
    
    class Config:
        orm_mode = True
