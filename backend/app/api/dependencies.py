from typing import Generator
from sqlalchemy.orm import Session
from app.database.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Database session dependency for FastAPI routes."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

