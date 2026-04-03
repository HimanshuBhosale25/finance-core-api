from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.financial_record import FinancialRecord, RecordType
from app.schemas.record import RecordCreate, RecordUpdate


def _active_records(db: Session):
    """Base query — always excludes soft-deleted records."""
    return db.query(FinancialRecord).filter(FinancialRecord.deleted_at.is_(None))


def get_records(
    db: Session,
    page: int = 1,
    limit: int = 20,
    type: Optional[RecordType] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
) -> dict:
    query = _active_records(db)

    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(FinancialRecord.date >= start_date)
    if end_date:
        query = query.filter(FinancialRecord.date <= end_date)
    if search:
        query = query.filter(FinancialRecord.notes.ilike(f"%{search}%"))

    total = query.count()
    records = (
        query.order_by(FinancialRecord.date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "data": records,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": max(1, -(-total // limit)),  # ceiling division
        },
    }


def get_record_by_id(db: Session, record_id: int) -> FinancialRecord:
    record = _active_records(db).filter(FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id {record_id} not found.",
        )
    return record


def create_record(db: Session, payload: RecordCreate, user_id: int) -> FinancialRecord:
    record = FinancialRecord(
        created_by=user_id,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record_id: int, payload: RecordUpdate) -> FinancialRecord:
    record = get_record_by_id(db, record_id)

    if payload.amount is not None:
        record.amount = payload.amount
    if payload.type is not None:
        record.type = payload.type
    if payload.category is not None:
        record.category = payload.category
    if payload.date is not None:
        record.date = payload.date
    if payload.notes is not None:
        record.notes = payload.notes

    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int) -> None:
    record = get_record_by_id(db, record_id)
    record.deleted_at = datetime.now(timezone.utc)
    db.commit()