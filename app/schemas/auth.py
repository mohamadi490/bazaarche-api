from pydantic import BaseModel, Field

from schemas.user import UserInDBBase


class BaseAuth(BaseModel):
    username: str = Field(min_length=3, max_length=50)

class LoginRequest(BaseAuth):
    password: str
    hasPassword: bool

class RegisterRequest(BaseAuth):
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserToken(Token):
    user: UserInDBBase
