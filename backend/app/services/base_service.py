"""
베이스 서비스 클래스 - 공통 기능 추상화
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """모든 서비스의 기본 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """서비스 처리 메서드 (추상 메서드)"""
        pass
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """공통 에러 처리"""
        self.logger.error(f"{context}: {error}", exc_info=True)


class TransactionProcessor(BaseService):
    """거래 내역 처리 추상 클래스"""
    
    @abstractmethod
    async def extract_data(self, source: Any) -> Dict[str, Any]:
        """소스에서 데이터 추출"""
        pass
    
    async def process(self, source: Any, user_id: str) -> Dict[str, Any]:
        """거래 내역 처리 프로세스"""
        try:
            # 데이터 추출
            extracted = await self.extract_data(source)
            
            # AI 분류 (서브클래스에서 구현 가능)
            if hasattr(self, 'classify_category'):
                classification = await self.classify_category(
                    extracted.get("original_text", ""),
                    extracted.get("amount")
                )
                extracted.update(classification)
            
            return extracted
        except Exception as e:
            self.handle_error(e, f"{self.__class__.__name__} 처리 중")
            raise

