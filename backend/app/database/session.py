from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.database.models.base import Base

def _ensure_db_dir(url: str):
    if "sqlite" in url:
        cleaned = url.split(":///")[-1]
        db_path = Path(cleaned)
        db_path.parent.mkdir(parents=True, exist_ok=True)

_ensure_db_dir(settings.DATABASE_SYNC_URL)

# High-performance, rock-solid SQLAlchemy engine
# Automatically configured for SQLite or PostgreSQL
engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_SYNC_URL else {},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    """FastAPI & service dependency for database sessions."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    """Initializes all database tables synchronously."""
    _ensure_db_dir(settings.DATABASE_SYNC_URL)
    Base.metadata.create_all(bind=engine)
