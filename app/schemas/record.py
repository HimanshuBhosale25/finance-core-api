from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.financial_record import RecordType


class RecordCreate(BaseModel):
    amount: Decimal
    type: RecordType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be blank")
        return v.strip()


class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v else v

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Category cannot be blank")
        return v.strip() if v else v


class RecordResponse(BaseModel):
    id: int
    created_by: int
    amount: Decimal
    type: RecordType
    category: str
    date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedRecords(BaseModel):
    data: list[RecordResponse]
    meta: dict