from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4

# Base class for SQLAlchemy's ORM models
# Actual tables will inherit from this class
class BaseModel(DeclarativeBase):
    """Base class for all SQLAlchemy's ORM models"""
    pass

class User(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_onupdate=func.now())