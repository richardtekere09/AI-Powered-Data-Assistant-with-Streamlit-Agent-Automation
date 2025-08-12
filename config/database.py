"""
Database configuration and connection management for AI Data Assistant
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ai_data_assistant")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres123")

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create Base here to avoid circular imports
Base = declarative_base()

# Create SQLAlchemy engine
try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,  # Set to True for SQL debugging
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None

# Create SessionLocal class
SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
)


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Ensures proper session cleanup.
    """
    if not SessionLocal:
        raise Exception("Database not configured properly")

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def test_database_connection():
    """Test database connectivity."""
    try:
        if not engine:
            return False, "Database engine not initialized"

        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {e}"


def init_database():
    """Initialize database tables."""
    try:
        if not engine:
            raise Exception("Database engine not available")

        # Create all tables using Base from this file
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def get_database_status():
    """Get current database status."""
    try:
        connection_ok, message = test_database_connection()
        if connection_ok:
            with get_db_session() as db:
                # Try a simple query to verify tables exist
                try:
                    # Import here to avoid circular imports
                    from models.user import User

                    user_count = db.query(User).count()
                    return {
                        "status": "connected",
                        "message": f"Database connected successfully. {user_count} users found.",
                        "url": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
                    }
                except ImportError:
                    return {
                        "status": "connected",
                        "message": "Database connected (models not yet imported).",
                        "url": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
                    }
        else:
            return {
                "status": "error",
                "message": message,
                "url": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database status check failed: {e}",
            "url": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
        }
