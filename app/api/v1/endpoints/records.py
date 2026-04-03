from typing import Optional
from fastapi import APIRouter, Query

from app.core.dependencies import DBSession, AnyAuthUser, AnalystUser, AdminUser
from app.models.financial_record import RecordType
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse, PaginatedRecords
from app.services import record_service

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.get("", response_model=PaginatedRecords)
def list_records(
    db: DBSession,
    current_user: AnyAuthUser,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    type: Optional[RecordType] = Query(default=None),
    category: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    search: Optional[str] = Query(default=None, description="Search in notes"),
):
    return record_service.get_records(
        db=db,
        page=page,
        limit=limit,
        type=type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )


@router.post("", response_model=RecordResponse, status_code=201)
def create_record(payload: RecordCreate, db: DBSession, current_user: AnalystUser):
    return record_service.create_record(db, payload, user_id=current_user.id)


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, db: DBSession, current_user: AnyAuthUser):
    return record_service.get_record_by_id(db, record_id)


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(record_id: int, payload: RecordUpdate, db: DBSession, current_user: AdminUser):
    return record_service.update_record(db, record_id, payload)


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: DBSession, current_user: AdminUser):
    record_service.delete_record(db, record_id)