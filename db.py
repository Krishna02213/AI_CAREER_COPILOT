import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use Railway/TiDB DATABASE_URL in production.
# If not available, fall back to a local SQLite database.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume.db")

# Configure engine differently for local SQLite vs deployed TiDB/MySQL
if DATABASE_URL.startswith("sqlite"):
    # Local development (SQLite)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    # Production deployment (Railway + TiDB Cloud)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={
            "ssl": {"ssl_mode": "VERIFY_IDENTITY"}
        }
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()