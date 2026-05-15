from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Replace <PASSWORD> with your actual TiDB Cloud password.
# URL-encode special characters in the password if needed.
DATABASE_URL = (
    "mysql+pymysql://21jgjbhQDEXMX11.root:W4hd4yBe3qMtHOPW"
    "@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/test"
)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            # On macOS this CA bundle is commonly available.
            "ca": "/etc/ssl/cert.pem"
        }
    }
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()