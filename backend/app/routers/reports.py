from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.routers.auth import get_current_user
from app.db import get_database
from app.services.ai_service import classify_category
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["리포트"])


@router.get("/generate", response_model=dict)
async def generate_monthly_report(
    month: str = Query(..., description="YYYY-MM 형식"),
    current_user: dict = Depends(get_current_user)
):
    """월간 리포트 생성"""
    try:
        # 월 파싱
        year, month_num = month.split("-")
        start_date = datetime(int(year), int(month_num), 1)
        if int(month_num) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month_num) + 1, 1)
        
        db = get_database()
        
        # 해당 월 거래 내역 조회
        transactions = await db.transactions.find({
            "user_id": ObjectId(current_user["id"]),
            "date": {"$gte": start_date, "$lt": end_date}
        }).to_list(length=10000)
        
        # 총 지출 계산
        total_spending = sum(t["amount"] for t in transactions)
        
        # 카테고리별 집계
        category_breakdown = {}
        for trans in transactions:
            category = trans.get("category", "기타")
            if category not in category_breakdown:
                category_breakdown[category] = {
                    "amount": 0,
                    "count": 0
                }
            category_breakdown[category]["amount"] += trans["amount"]
            category_breakdown[category]["count"] += 1
        
        # 비율 계산
        for cat_data in category_breakdown.values():
            if total_spending > 0:
                cat_data["percentage"] = (cat_data["amount"] / total_spending) * 100
            else:
                cat_data["percentage"] = 0
        
        # 전월 데이터 조회
        prev_start = start_date - timedelta(days=32)
        prev_start = datetime(prev_start.year, prev_start.month, 1)
        prev_end = start_date
        
        prev_transactions = await db.transactions.find({
            "user_id": ObjectId(current_user["id"]),
            "date": {"$gte": prev_start, "$lt": prev_end}
        }).to_list(length=10000)
        
        previous_month_total = sum(t["amount"] for t in prev_transactions)
        
        # 증감률 계산
        if previous_month_total > 0:
            change_percentage = ((total_spending - previous_month_total) / previous_month_total) * 100
        else:
            change_percentage = 0 if total_spending == 0 else 100
        
        # AI 인사이트 생성
        insights = await generate_insights(
            category_breakdown,
            total_spending,
            previous_month_total,
            change_percentage
        )
        
        # 리포트 저장
        report_doc = {
            "user_id": ObjectId(current_user["id"]),
            "month": month,
            "total_spending": total_spending,
            "category_breakdown": category_breakdown,
            "insights": insights,
            "comparison": {
                "previous_month_total": previous_month_total,
                "change_percentage": change_percentage
            },
            "generated_at": datetime.utcnow()
        }
        
        # 기존 리포트가 있으면 업데이트, 없으면 생성
        await db.monthly_reports.update_one(
            {
                "user_id": ObjectId(current_user["id"]),
                "month": month
            },
            {"$set": report_doc},
            upsert=True
        )
        
        # 응답 형식 변환
        report_response = {
            "id": month,
            "user_id": current_user["id"],
            "month": month,
            "total_spending": total_spending,
            "category_breakdown": category_breakdown,
            "insights": insights,
            "comparison": {
                "previous_month_total": previous_month_total,
                "change_percentage": change_percentage
            },
            "generated_at": report_doc["generated_at"].isoformat()
        }
        
        return report_response
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"리포트 생성 중 오류가 발생했습니다: {str(e)}"
        )


async def generate_insights(
    category_breakdown: Dict,
    total_spending: float,
    previous_month_total: float,
    change_percentage: float
) -> List[Dict]:
    """AI 인사이트 생성"""
    insights = []
    
    # 총 지출 변화 인사이트
    if abs(change_percentage) > 10:
        if change_percentage > 0:
            insights.append({
                "type": "warning",
                "message": f"이번 달 지출이 전월 대비 {change_percentage:.1f}% 증가했습니다. 소비 패턴을 확인해보세요.",
                "generated_by": "ai"
            })
        else:
            insights.append({
                "type": "success",
                "message": f"이번 달 지출이 전월 대비 {abs(change_percentage):.1f}% 감소했습니다. 좋은 소비 습관을 유지하세요!",
                "generated_by": "ai"
            })
    
    # 카테고리별 인사이트
    if category_breakdown:
        sorted_categories = sorted(
            category_breakdown.items(),
            key=lambda x: x[1]["amount"],
            reverse=True
        )
        
        top_category = sorted_categories[0]
        if top_category[1]["percentage"] > 40:
            insights.append({
                "type": "info",
                "message": f"{top_category[0]} 지출이 전체의 {top_category[1]['percentage']:.1f}%를 차지합니다. 다른 카테고리와 균형을 맞춰보세요.",
                "generated_by": "ai"
            })
    
    # 인사이트가 없으면 기본 메시지
    if not insights:
        insights.append({
            "type": "info",
            "message": "이번 달 소비 패턴을 분석했습니다. 꾸준히 기록하여 더 나은 인사이트를 받아보세요!",
            "generated_by": "ai"
        })
    
    return insights


@router.get("/{report_id}", response_model=dict)
async def get_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """리포트 조회"""
    db = get_database()
    
    # 리포트 조회 (report_id는 month 형식)
    report = await db.monthly_reports.find_one({
        "user_id": ObjectId(current_user["id"]),
        "month": report_id
    })
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="리포트를 찾을 수 없습니다."
        )
    
    # 응답 형식 변환
    return {
        "id": str(report["_id"]),
        "user_id": current_user["id"],
        "month": report["month"],
        "total_spending": report["total_spending"],
        "category_breakdown": report["category_breakdown"],
        "insights": report["insights"],
        "comparison": report["comparison"],
        "generated_at": report["generated_at"].isoformat()
    }

