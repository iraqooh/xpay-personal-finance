from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional, Literal

class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = "USD"
    date: datetime
    description: Optional[str] = None
    category_id: Optional[UUID]

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)