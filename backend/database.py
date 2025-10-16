# backend/database.py
import os
from sqlmodel import SQLModel, create_engine, Session

# Use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobhunter.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

def get_db():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session