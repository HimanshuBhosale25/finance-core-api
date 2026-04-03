from decimal import Decimal
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    total_records: int


class CategoryBreakdownItem(BaseModel):
    category: str
    type: str
    total: Decimal
    count: int


class MonthlyTrendItem(BaseModel):
    year: int
    month: int
    income: Decimal
    expenses: Decimal
    net: Decimal


class RecentActivityItem(BaseModel):
    id: int
    amount: Decimal
    type: str
    category: str
    date: str
    notes: str | None


class DashboardResponse(BaseModel):
    summary: SummaryResponse
    category_breakdown: list[CategoryBreakdownItem]
    monthly_trends: list[MonthlyTrendItem]
    recent_activity: list[RecentActivityItem]