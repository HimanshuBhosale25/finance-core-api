from decimal import Decimal
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord, RecordType


def get_summary(db: Session) -> dict:
    result = db.query(
        func.coalesce(
            func.sum(case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)),
            Decimal("0.00")
        ).label("total_income"),
        func.coalesce(
            func.sum(case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)),
            Decimal("0.00")
        ).label("total_expenses"),
        func.count(FinancialRecord.id).label("total_records"),
    ).filter(FinancialRecord.deleted_at.is_(None)).one()

    return {
        "total_income": result.total_income,
        "total_expenses": result.total_expenses,
        "net_balance": result.total_income - result.total_expenses,
        "total_records": result.total_records,
    }


def get_category_breakdown(db: Session) -> list[dict]:
    rows = (
        db.query(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.id).label("count"),
        )
        .filter(FinancialRecord.deleted_at.is_(None))
        .group_by(FinancialRecord.category, FinancialRecord.type)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )
    return [
        {"category": r.category, "type": r.type.value, "total": r.total, "count": r.count}
        for r in rows
    ]


def get_monthly_trends(db: Session) -> list[dict]:
    rows = (
        db.query(
            func.year(FinancialRecord.date).label("year"),
            func.month(FinancialRecord.date).label("month"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)),
                Decimal("0.00")
            ).label("income"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)),
                Decimal("0.00")
            ).label("expenses"),
        )
        .filter(FinancialRecord.deleted_at.is_(None))
        .group_by(func.year(FinancialRecord.date), func.month(FinancialRecord.date))
        .order_by(func.year(FinancialRecord.date), func.month(FinancialRecord.date))
        .all()
    )
    return [
        {
            "year": r.year,
            "month": r.month,
            "income": r.income,
            "expenses": r.expenses,
            "net": r.income - r.expenses,
        }
        for r in rows
    ]


def get_recent_activity(db: Session, limit: int = 10) -> list[dict]:
    records = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.deleted_at.is_(None))
        .order_by(FinancialRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "amount": r.amount,
            "type": r.type.value,
            "category": r.category,
            "date": str(r.date),
            "notes": r.notes,
        }
        for r in records
    ]