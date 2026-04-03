from fastapi import APIRouter, Query

from app.core.dependencies import DBSession, AnalystUser
from app.schemas.dashboard import (
    SummaryResponse,
    DashboardResponse,
)
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary(db: DBSession, current_user: AnalystUser):
    return dashboard_service.get_summary(db)


@router.get("/category-breakdown")
def get_category_breakdown(db: DBSession, current_user: AnalystUser):
    return dashboard_service.get_category_breakdown(db)


@router.get("/trends")
def get_monthly_trends(db: DBSession, current_user: AnalystUser):
    return dashboard_service.get_monthly_trends(db)


@router.get("/recent-activity")
def get_recent_activity(
    db: DBSession,
    current_user: AnalystUser,
    limit: int = Query(default=10, ge=1, le=50),
):
    return dashboard_service.get_recent_activity(db, limit=limit)


@router.get("", response_model=DashboardResponse)
def get_full_dashboard(db: DBSession, current_user: AnalystUser):
    """Single endpoint that returns everything at once."""
    return {
        "summary": dashboard_service.get_summary(db),
        "category_breakdown": dashboard_service.get_category_breakdown(db),
        "monthly_trends": dashboard_service.get_monthly_trends(db),
        "recent_activity": dashboard_service.get_recent_activity(db),
    }