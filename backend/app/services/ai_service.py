from anthropic import Anthropic
from app.config import settings
from typing import Dict, Optional
import logging
import re
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CategoryClassifier(ABC):
    """카테고리 분류 추상 인터페이스"""
    
    @abstractmethod
    async def classify(self, text: str, amount: Optional[float] = None) -> Dict[str, any]:
        """카테고리를 분류합니다"""
        pass


class ClaudeCategoryClassifier(CategoryClassifier):
    """Claude API를 사용한 카테고리 분류"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.categories = [
            "식비 (외식, 배달, 카페 등)",
            "교통비 (대중교통, 택시, 주유 등)",
            "쇼핑 (의류, 전자제품, 생활용품 등)",
            "문화/여가 (영화, 공연, 취미 등)",
            "의료/건강 (병원, 약국, 헬스 등)",
            "주거/통신 (월세, 관리비, 인터넷 등)",
            "교육 (학원, 서적 등)",
            "기타"
        ]
        self.category_map = {
            "식비": "식비",
            "교통비": "교통비",
            "쇼핑": "쇼핑",
            "문화/여가": "문화/여가",
            "문화여가": "문화/여가",
            "의료/건강": "의료/건강",
            "의료건강": "의료/건강",
            "주거/통신": "주거/통신",
            "주거통신": "주거/통신",
            "교육": "교육",
            "기타": "기타"
        }
    
    async def classify(self, text: str, amount: Optional[float] = None) -> Dict[str, any]:
        """Claude API를 사용하여 카테고리 분류"""
        prompt = self._build_prompt(text, amount)
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text.strip()
            result = self._parse_response(response_text, text)
            return result
            
        except Exception as e:
            logger.error(f"Claude API 분류 오류: {e}")
            raise
    
    def _build_prompt(self, text: str, amount: Optional[float]) -> str:
        """프롬프트 생성"""
        return f"""다음 소비 내역을 분석하여 카테고리를 분류해주세요.

소비 내역: {text}
금액: {amount if amount else "알 수 없음"}

다음 카테고리 중 하나를 선택하세요:
{chr(10).join(f"- {cat}" for cat in self.categories)}

응답 형식은 JSON으로 다음과 같이 해주세요:
{{
    "category": "카테고리명 (예: 식비, 교통비 등)",
    "sub_category": "세부 카테고리 (예: 카페, 택시 등, 없으면 null)",
    "description": "설명 (원본 텍스트에서 추출)",
    "merchant": "거래처명 (있으면 추출, 없으면 null)",
    "confidence": 0.0-1.0 사이의 신뢰도
}}

JSON만 응답하고 다른 설명은 하지 마세요."""
    
    def _parse_response(self, response_text: str, original_text: str) -> Dict[str, any]:
        """응답 파싱"""
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            import json
            result = json.loads(json_match.group())
            
            category = result.get("category", "기타")
            result["category"] = self.category_map.get(category, category)
            
            return {
                "category": result.get("category", "기타"),
                "sub_category": result.get("sub_category"),
                "description": result.get("description", original_text),
                "merchant": result.get("merchant"),
                "confidence": float(result.get("confidence", 0.8))
            }
        else:
            logger.warning("AI 응답에서 JSON을 찾을 수 없습니다.")
            raise ValueError("AI 응답 파싱 실패")


class RuleBasedCategoryClassifier(CategoryClassifier):
    """규칙 기반 카테고리 분류 (폴백)"""
    
    def __init__(self):
        self.category_keywords = {
            "식비": ["스타벅스", "카페", "커피", "맥도날드", "버거킹", "배달", "배민", "요기요", "식당", "레스토랑", "치킨", "피자"],
            "교통비": ["택시", "버스", "지하철", "기차", "주유", "주유소", "gs25", "cu", "편의점"],
            "쇼핑": ["옷", "의류", "전자", "스마트폰", "컴퓨터", "마트", "이마트", "롯데마트"],
            "문화/여가": ["영화", "공연", "콘서트", "게임", "넷플릭스", "왓챠"],
            "의료/건강": ["병원", "약국", "약", "헬스", "체육관"],
            "주거/통신": ["월세", "관리비", "전기", "가스", "인터넷", "통신", "kt", "sk", "lg"],
            "교육": ["학원", "교재", "책", "서적"]
        }
    
    async def classify(self, text: str, amount: Optional[float] = None) -> Dict[str, any]:
        """규칙 기반 분류"""
        text_lower = text.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return {
                    "category": category,
                    "sub_category": None,
                    "description": text,
                    "merchant": None,
                    "confidence": 0.7
                }
        
        return {
            "category": "기타",
            "sub_category": None,
            "description": text,
            "merchant": None,
            "confidence": 0.5
        }


class CategoryClassifierFactory:
    """카테고리 분류기 팩토리 (다형성 구현)"""
    
    _classifier: Optional[CategoryClassifier] = None
    
    @classmethod
    def get_classifier(cls) -> CategoryClassifier:
        """적절한 분류기 인스턴스 반환"""
        if cls._classifier is None:
            if settings.anthropic_api_key:
                cls._classifier = ClaudeCategoryClassifier(settings.anthropic_api_key)
                logger.info("Claude API 분류기 사용")
            else:
                cls._classifier = RuleBasedCategoryClassifier()
                logger.warning("Claude API 키가 설정되지 않았습니다. 규칙 기반 분류를 사용합니다.")
        return cls._classifier


# 전역 함수 (하위 호환성 유지)
async def classify_category(text: str, amount: Optional[float] = None) -> Dict[str, any]:
    """카테고리 분류 (팩토리 패턴 사용)"""
    classifier = CategoryClassifierFactory.get_classifier()
    return await classifier.classify(text, amount)


def default_classify(text: str, amount: Optional[float] = None) -> Dict[str, any]:
    """기본 규칙 기반 분류 (하위 호환성)"""
    classifier = RuleBasedCategoryClassifier()
    import asyncio
    return asyncio.run(classifier.classify(text, amount))


async def extract_transaction_info(text: str) -> Dict[str, any]:
    """
    텍스트에서 거래 정보 추출 (날짜, 금액, 상호명 등)
    """
    # 금액 추출 (숫자 + 원)
    amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*원'
    amount_match = re.search(amount_pattern, text)
    amount = None
    if amount_match:
        amount_str = amount_match.group(1).replace(',', '')
        try:
            amount = float(amount_str)
        except:
            pass
    
    # 날짜 추출 (YYYY-MM-DD, YYYY년 MM월 DD일 등)
    date_patterns = [
        r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
    ]
    
    date = datetime.now()  # 기본값: 오늘
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                year, month, day = match.groups()
                date = datetime(int(year), int(month), int(day))
                break
            except:
                pass
    
    # 상호명 추출 (금액 앞의 텍스트)
    merchant = None
    if amount_match:
        before_amount = text[:amount_match.start()].strip()
        # 일반적인 상호명 패턴
        merchant_match = re.search(r'([가-힣a-zA-Z\s]+)', before_amount)
        if merchant_match:
            merchant = merchant_match.group(1).strip()
    
    return {
        "amount": amount,
        "date": date,
        "merchant": merchant,
        "original_text": text
    }
