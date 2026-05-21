"""
app/db/database.py
──────────────────
SQLAlchemy engine + session factory.
Tables are created automatically on startup via Base.metadata.create_all().
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# create_engine handles connection pooling automatically.
# pool_pre_ping=True drops stale connections (important for Railway/Supabase).
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency – yields a DB session then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
