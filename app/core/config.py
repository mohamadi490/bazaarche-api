from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    debug: bool = os.getenv("DEBUG")
    access_token_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

settings = Settings()