import os
from sqlmodel import SQLModel, create_engine, Session
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL with proper fallbacks and validation"""
    database_url = os.getenv("DATABASE_URL")
    
    # If DATABASE_URL is not set or empty, use SQLite
    if not database_url:
        logger.warning("DATABASE_URL not set, using SQLite fallback")
        return "sqlite:///./jobhunter.db"
    
    # Ensure PostgreSQL URLs use postgresql:// instead of postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        logger.info("Fixed PostgreSQL URL format")
    
    return database_url

DATABASE_URL = get_database_url()

try:
    engine = create_engine(DATABASE_URL, echo=False)
    logger.info(f"Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    logger.info("Falling back to SQLite...")
    DATABASE_URL = "sqlite:///./jobhunter.db"
    engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    """Create all database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")

def get_db():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
