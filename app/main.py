from fastapi import FastAPI
from db.base import Base
from db.session import engine
from routers.v1.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router, prefix="/api/v1")