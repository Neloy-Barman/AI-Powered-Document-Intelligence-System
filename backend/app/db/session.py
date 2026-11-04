from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import DATABASE_URL

database_url = DATABASE_URL
if database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
engine = create_engine(database_url, pool_pre_ping=True) if database_url else None

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """FastAPI dependency for database sessions."""
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
