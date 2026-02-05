from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with SSL mode=require for Neon
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",  # Enforce SSL for Neon PostgreSQL
        "connect_timeout": 10  # Set connection timeout
    },
    pool_pre_ping=True,  # Verify connections before use
    echo=True,  # Enable SQL logging for debugging
    pool_size=5,  # Set initial pool size
    max_overflow=10,  # Set max overflow
    pool_timeout=30,  # Set pool timeout
    pool_recycle=3600  # Recycle connections after 1 hour
)

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """Create database tables"""
    from src.models.user import User
    from src.models.task import Task
    from src.models.trash_bin import TrashBin
    from src.models.chat import Conversation, Message
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)