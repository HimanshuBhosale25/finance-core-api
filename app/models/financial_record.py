import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, Text, DECIMAL, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class RecordType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    type = Column(Enum(RecordType), nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    creator = relationship("User", backref="records")

    __table_args__ = (
        Index("idx_record_type", "type"),
        Index("idx_record_category", "category"),
        Index("idx_record_date", "date"),
        Index("idx_record_created_by", "created_by"),
        Index("idx_record_deleted_at", "deleted_at"),
    )