from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Read database URL from environment variable
DATABASE_URL = os.getenv("mysql+pymysql://21jgjbhQDEXMX11.root:W4hd4yBe3qMtHOPW@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/test")

# Create database engine (without local SSL certificate path)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()