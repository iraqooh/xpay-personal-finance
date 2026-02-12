from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4

# Base class for SQLAlchemy's ORM models
# Actual tables will inherit from this class
class BaseModel(DeclarativeBase):
    """Base class for all SQLAlchemy's ORM models"""
    pass

# User model representing a user in the system
class User(BaseModel):
    __tablename__ = "users"

    # Unique identifier for the user, using UUID for better security and scalability
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    transaction = relationship("Transaction", back_populates="user")

class Category(BaseModel):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    transaction = relationship("Transaction", back_populates="category")

class Transaction(BaseModel):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String(3), default="USD")
    date = Column(DateTime, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="transaction")
    user = relationship("User", back_populates="transaction")