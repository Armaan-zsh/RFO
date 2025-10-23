"""
Database models and connection for rocket fuel optimization.
"""
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL - use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rocket_optimizer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Experiment(Base):
    """Experiment model for storing experiment parameters."""
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, index=True)
    params = Column(JSON, nullable=False)
    status = Column(String, default="queued")
    created_at = Column(DateTime, default=datetime.utcnow)


class Result(Base):
    """Result model for storing experiment results."""
    __tablename__ = "results"
    
    experiment_id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)


def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables on import
create_tables()