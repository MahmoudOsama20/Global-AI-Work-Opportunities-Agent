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

def _migrate_columns():
    """Ensures newly added columns are present in existing SQLite tables."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "opportunities" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("opportunities")}
        new_columns = [
            ("collected_at", "DATETIME"),
            ("freshness_status", "VARCHAR(32) DEFAULT 'unknown_date'"),
            ("freshness_score", "FLOAT DEFAULT 0.0"),
            ("seniority_compatibility", "VARCHAR(64)"),
            ("seniority_mismatch_reason", "TEXT"),
            ("cv_match_breakdown", "JSON DEFAULT '{}'"),
        ]
        with engine.begin() as conn:
            for col_name, col_type in new_columns:
                if col_name not in columns:
                    conn.execute(text(f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}"))

def init_db():
    """Initializes all database tables synchronously and applies light migrations."""
    _ensure_db_dir(settings.DATABASE_SYNC_URL)
    Base.metadata.create_all(bind=engine)
    _migrate_columns()
