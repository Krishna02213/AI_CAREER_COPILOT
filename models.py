from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


# ---------------- USER MODEL ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    # One user can have many reports
    reports = relationship(
        "Report",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ---------------- REPORT MODEL ----------------
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking to users.id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Original resume text
    resume_text = Column(Text, nullable=False)

    # JSON result stored as string
    results = Column(Text, nullable=False)

    # Relationship back to User
    user = relationship(
        "User",
        back_populates="reports"
    )