from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.ai_service import classify_category, extract_transaction_info
from app.services.ocr_service import extract_text_from_image, parse_receipt
from app.services.file_service import parse_csv_file
from app.services.transaction_service import TransactionService
from app.routers.auth import get_current_user
from app.db import get_database
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["거래 내역"])
security = HTTPBearer()

# 서비스 인스턴스 (의존성 주입)
def get_transaction_service() -> TransactionService:
    """거래 서비스 인스턴스 반환"""
    return TransactionService()


@router.post("/text", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transaction_from_text(
    text: str = Form(...),
    current_user: dict = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """텍스트로 거래 내역 입력"""
    try:
        # 텍스트에서 정보 추출
        extracted = await extract_transaction_info(text)
        
        if not extracted["amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="금액을 찾을 수 없습니다. 금액을 포함하여 입력해주세요."
            )
        
        # 거래 내역 생성 (서비스 사용)
        transaction_id = await service.create_transaction(
            user_id=current_user["id"],
            extracted_data=extracted,
            source_type="text",
            original_text=text
        )
        
        return {
            "id": transaction_id,
            "message": "거래 내역이 성공적으로 추가되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 생성 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"거래 내역 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/image", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transaction_from_image(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """이미지(영수증)로 거래 내역 입력"""
    try:
        # 이미지 파일 읽기
        image_bytes = await image.read()
        
        # OCR로 텍스트 추출
        ocr_text = await extract_text_from_image(image_bytes)
        
        if not ocr_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지에서 텍스트를 추출할 수 없습니다. 더 선명한 이미지를 업로드해주세요."
            )
        
        # 영수증 파싱
        parsed = await parse_receipt(ocr_text)
        
        if not parsed["amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="영수증에서 금액을 찾을 수 없습니다."
            )
        
        # OCR 데이터 추가
        parsed["ocr_data"] = {"text": ocr_text}
        
        # 거래 내역 생성 (서비스 사용)
        transaction_id = await service.create_transaction(
            user_id=current_user["id"],
            extracted_data=parsed,
            source_type="image",
            original_text=ocr_text
        )
        
        return {
            "id": transaction_id,
            "message": "영수증이 성공적으로 분석되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"이미지 처리 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/file", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transactions_from_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """CSV/Excel 파일로 거래 내역 일괄 입력"""
    try:
        # 파일 읽기
        file_bytes = await file.read()
        
        # 파일 파싱
        transactions_data = await parse_csv_file(file_bytes, file.filename)
        
        if not transactions_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일에서 거래 내역을 찾을 수 없습니다."
            )
        
        # 일괄 생성 (서비스 사용)
        inserted_count = await service.create_transactions_batch(
            user_id=current_user["id"],
            transactions_data=transactions_data,
            source_type="csv"
        )
        
        return {
            "count": inserted_count,
            "message": f"{inserted_count}건의 거래 내역이 성공적으로 추가되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 처리 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("", response_model=dict)
async def get_transactions(
    month: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """거래 내역 조회"""
    db = get_database()
    
    # 쿼리 조건
    query = {"user_id": ObjectId(current_user["id"])}
    
    # 월 필터
    if month:
        year, month_num = month.split("-")
        start_date = datetime(int(year), int(month_num), 1)
        if int(month_num) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month_num) + 1, 1)
        query["date"] = {"$gte": start_date, "$lt": end_date}
    
    # 카테고리 필터
    if category:
        query["category"] = category
    
    # 거래 내역 조회
    cursor = db.transactions.find(query).sort("date", -1)
    transactions = await cursor.to_list(length=1000)
    
    # 응답 형식 변환
    transaction_list = []
    for trans in transactions:
        transaction_list.append({
            "_id": str(trans["_id"]),
            "user_id": str(trans["user_id"]),
            "date": trans["date"].isoformat(),
            "amount": trans["amount"],
            "category": trans["category"],
            "sub_category": trans.get("sub_category"),
            "description": trans.get("description"),
            "merchant": trans.get("merchant"),
            "source_type": trans.get("source_type", "text"),
            "ai_confidence": trans.get("ai_confidence"),
            "created_at": trans["created_at"].isoformat(),
            "metadata": trans.get("metadata")
        })
    
    return {
        "transactions": transaction_list,
        "count": len(transaction_list)
    }


@router.put("/{transaction_id}", response_model=dict)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """거래 내역 수정"""
    db = get_database()
    
    # 거래 내역 확인
    transaction = await db.transactions.find_one({
        "_id": ObjectId(transaction_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="거래 내역을 찾을 수 없습니다."
        )
    
    # 업데이트 데이터 준비
    update_data = {}
    if transaction_update.date:
        update_data["date"] = transaction_update.date
    if transaction_update.amount:
        update_data["amount"] = transaction_update.amount
    if transaction_update.category:
        update_data["category"] = transaction_update.category
    if transaction_update.sub_category is not None:
        update_data["sub_category"] = transaction_update.sub_category
    if transaction_update.description is not None:
        update_data["description"] = transaction_update.description
    if transaction_update.merchant is not None:
        update_data["merchant"] = transaction_update.merchant
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 데이터가 없습니다."
        )
    
    # 업데이트 실행
    await db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": update_data}
    )
    
    return {
        "message": "거래 내역이 성공적으로 수정되었습니다."
    }


@router.delete("/{transaction_id}", response_model=dict)
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """거래 내역 삭제"""
    db = get_database()
    
    # 거래 내역 확인 및 삭제
    result = await db.transactions.delete_one({
        "_id": ObjectId(transaction_id),
        "user_id": ObjectId(current_user["id"])
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="거래 내역을 찾을 수 없습니다."
        )
    
    return {
        "message": "거래 내역이 성공적으로 삭제되었습니다."
    }

