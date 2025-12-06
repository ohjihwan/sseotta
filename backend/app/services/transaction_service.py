"""
거래 내역 서비스 - 거래 내역 생성 로직 캡슐화
"""
from app.services.base_service import TransactionProcessor
from app.services.ai_service import classify_category
from app.db import get_database
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TransactionService(TransactionProcessor):
    """거래 내역 생성 및 관리 서비스"""
    
    def __init__(self):
        super().__init__()
        self.db = get_database()
    
    async def extract_data(self, source: Any) -> Dict[str, Any]:
        """추상 메서드 구현 - 서브클래스에서 오버라이드"""
        raise NotImplementedError("서브클래스에서 구현해야 합니다")
    
    async def classify_category(self, text: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """AI 카테고리 분류"""
        return await classify_category(text, amount)
    
    async def create_transaction(
        self,
        user_id: str,
        extracted_data: Dict[str, Any],
        source_type: str,
        original_text: Optional[str] = None
    ) -> str:
        """
        거래 내역 생성 (캡슐화된 공통 로직)
        
        Args:
            user_id: 사용자 ID
            extracted_data: 추출된 거래 데이터
            source_type: 소스 타입 (text, image, csv)
            original_text: 원본 텍스트
        
        Returns:
            생성된 거래 내역 ID
        """
        # AI 분류
        ai_result = await self.classify_category(
            extracted_data.get("original_text", original_text or ""),
            extracted_data.get("amount")
        )
        
        # 거래 내역 문서 생성
        transaction_doc = {
            "user_id": ObjectId(user_id),
            "date": extracted_data.get("date", datetime.utcnow()),
            "amount": extracted_data["amount"],
            "category": ai_result["category"],
            "sub_category": ai_result.get("sub_category"),
            "description": ai_result.get("description") or extracted_data.get("description") or extracted_data.get("merchant") or "",
            "merchant": ai_result.get("merchant") or extracted_data.get("merchant"),
            "source_type": source_type,
            "ai_confidence": ai_result.get("confidence", 0.8),
            "created_at": datetime.utcnow(),
            "metadata": {
                "original_text": original_text or extracted_data.get("original_text", "")
            }
        }
        
        # 이미지 소스인 경우 OCR 데이터 추가
        if source_type == "image" and extracted_data.get("ocr_data"):
            transaction_doc["metadata"]["ocr_data"] = extracted_data["ocr_data"]
        
        # 데이터베이스에 저장
        result = await self.db.transactions.insert_one(transaction_doc)
        return str(result.inserted_id)
    
    async def create_transactions_batch(
        self,
        user_id: str,
        transactions_data: list,
        source_type: str = "csv"
    ) -> int:
        """
        여러 거래 내역 일괄 생성
        
        Returns:
            성공적으로 생성된 거래 내역 수
        """
        inserted_count = 0
        
        for trans_data in transactions_data:
            try:
                await self.create_transaction(
                    user_id=user_id,
                    extracted_data=trans_data,
                    source_type=source_type,
                    original_text=trans_data.get("original_text")
                )
                inserted_count += 1
            except Exception as e:
                self.logger.warning(f"거래 내역 저장 오류: {e}")
                continue
        
        return inserted_count

