"""Database connection and session management"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from loguru import logger

from src.db.schema import Base


# Database configuration
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "order_return.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database(force_recreate: bool = False) -> None:
    """
    Initialize the database by creating all tables.

    Args:
        force_recreate: If True, drop all existing tables and recreate them.
    """
    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    if force_recreate and DB_PATH.exists():
        logger.warning(f"Dropping existing database at {DB_PATH}")
        DB_PATH.unlink()

    # Create all tables
    logger.info(f"Creating database tables at {DB_PATH}")
    Base.metadata.create_all(bind=engine)
    logger.success("Database initialized successfully")


def get_session() -> Session:
    """
    Get a new database session.

    Returns:
        SQLAlchemy Session instance

    Note:
        Caller is responsible for closing the session.
    """
    return SessionLocal()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        SQLAlchemy Session instance

    Example:
        with get_db_session() as session:
            customers = session.query(Customer).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def reset_database() -> None:
    """
    Drop all tables and recreate the database schema.
    Useful for testing and development.
    """
    logger.warning("Resetting database - all data will be lost!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.success("Database reset complete")


def check_database_exists() -> bool:
    """
    Check if the database file exists.

    Returns:
        True if database file exists, False otherwise
    """
    return DB_PATH.exists()


def get_database_path() -> Path:
    """
    Get the path to the database file.

    Returns:
        Path object pointing to the database file
    """
    return DB_PATH
