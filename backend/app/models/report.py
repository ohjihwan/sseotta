from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from bson import ObjectId


class Insight(BaseModel):
    type: str  # "warning" | "info" | "success"
    message: str
    generated_by: str = "ai"


class Comparison(BaseModel):
    previous_month_total: float
    change_percentage: float


class CategoryBreakdown(BaseModel):
    amount: float
    percentage: float
    count: int


class MonthlyReport(BaseModel):
    id: str
    user_id: str
    month: str  # YYYY-MM
    total_spending: float
    category_breakdown: Dict[str, CategoryBreakdown]
    insights: List[Insight]
    comparison: Comparison
    generated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}


class ReportResponse(MonthlyReport):
    pass

