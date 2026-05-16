import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Read database URL from Railway environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with SSL enabled for TiDB Cloud
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