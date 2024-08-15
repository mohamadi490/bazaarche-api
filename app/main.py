from fastapi import FastAPI
from db.base import Base
from db.session import engine
from routers.v1.users import router as users_router
from routers.v1.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")