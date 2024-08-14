from sqlalchemy.ext.declarative import declarative_base
from .session import SessionLocal
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()