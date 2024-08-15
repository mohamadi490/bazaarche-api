from pydantic import BaseModel


class AuthValidate(BaseModel):
    username: str
