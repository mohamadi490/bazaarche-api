from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.v1.users import user_router
from routers.v1.auth import auth_router
from routers.v1.roles import role_router
from routers.v1.category import category_router
from routers.v1.product import admin_product_router
from routers.v1.media import media_router
from routers.v1.cart import cart_router
from routers.v1.address import address_router
from routers.v1.shipping import shipping_router
from routers.v1.setting import setting_router
from routers.v1.order import order_router
from routers.v1.transaction import transaction_router
from routers.v1.product_home import product_router
import os

# Base.metadata.create_all(bind=engine)

app = FastAPI()

# اطمینان حاصل کن که مسیر uploads وجود داره
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# اضافه کردن مسیر استاتیک
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(admin_product_router, prefix="/api/v1/admin")
app.include_router(product_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(address_router, prefix="/api/v1")
app.include_router(shipping_router, prefix="/api/v1")
app.include_router(setting_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(transaction_router, prefix="/api/v1")