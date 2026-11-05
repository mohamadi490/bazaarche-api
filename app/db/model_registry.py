# app/db/model_registry.py
"""
هیچ منطقی اینجا نیست — فقط Import برای ثبت مدل‌ها در Base.metadata.
هر بار یک ماژول models.py واقعی نوشتید، همین‌جا اضافه‌اش کنید،
وگرنه Alembic آن جدول را نمی‌بیند.
"""

from app.db.base import Base  # noqa: F401
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.users import models as users_models  # noqa: F401

# from app.modules.catalog import models as catalog_models  # noqa: F401
# ... به‌ترتیب پیاده‌سازی هر ماژول، این خط را از کامنت خارج/اضافه کنید
