import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use Railway/TiDB DATABASE_URL in production.
# If not available, fall back to a local SQLite database.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume.db")

# Standardize database prefixes for SQLAlchemy 1.4+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
elif DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Configure connection arguments based on database engine
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    # Local development (SQLite)
    connect_args["check_same_thread"] = False
elif "tidb" in DATABASE_URL or os.getenv("DB_SSL_VERIFY") == "true":
    # Special SSL handling for TiDB Cloud if specified or detected
    connect_args["ssl"] = {"ssl_mode": "VERIFY_IDENTITY"}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args if connect_args else {}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()