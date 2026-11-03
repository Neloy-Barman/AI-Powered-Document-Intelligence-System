from backend.app.db.base import Base
from backend.app.db.session import engine


def ensure_tables() -> None:
    """Create database tables if they do not already exist."""
    if engine is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    Base.metadata.create_all(bind=engine)
