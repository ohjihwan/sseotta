from PIL import Image
import easyocr
from app.config import settings
from typing import Dict, Optional
import logging
import io
import re
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class OCRService:
    """OCR 서비스 클래스 (캡슐화)"""
    
    _instance = None
    _reader = None
    
    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._reader is None:
            logger.info(f"EasyOCR 리더 초기화 중... (한국어, 영어, GPU: {settings.easyocr_gpu})")
            self._reader = easyocr.Reader(['ko', 'en'], gpu=settings.easyocr_gpu)
            logger.info("EasyOCR 리더 초기화 완료")
    
    @property
    def reader(self):
        """리더 인스턴스 반환"""
        return self._reader
    
    async def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        이미지에서 텍스트 추출 (OCR)
        """
        try:
            # 이미지를 numpy 배열로 변환
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            # EasyOCR로 텍스트 추출
            results = self.reader.readtext(image_array)
            
            # 추출된 텍스트 결합
            text_lines = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # 신뢰도 50% 이상만 사용
                    text_lines.append(text)
            
            extracted_text = '\n'.join(text_lines)
            
            if not extracted_text.strip():
                raise Exception("이미지에서 텍스트를 찾을 수 없습니다.")
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"OCR 처리 오류: {e}")
            raise Exception(f"이미지에서 텍스트를 추출할 수 없습니다: {str(e)}")
    
    async def parse_receipt(self, text: str) -> Dict[str, any]:
        """
        영수증 텍스트를 파싱하여 거래 정보 추출
        """
        # 금액 추출
        amount_patterns = [
            r'합계[:\s]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'총액[:\s]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*원',
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    break
                except:
                    pass
        
        # 날짜 추출
        date_patterns = [
            r'(\d{4})[년\.\-/](\d{1,2})[월\.\-/](\d{1,2})',
            r'(\d{2})[년\.\-/](\d{1,2})[월\.\-/](\d{1,2})',
        ]
        
        date = datetime.now()
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year, month, day = match.groups()
                    if len(year) == 2:
                        year = '20' + year
                    date = datetime(int(year), int(month), int(day))
                    break
                except:
                    pass
        
        # 상호명 추출 (첫 번째 줄 또는 특정 패턴)
        merchant = None
        lines = text.split('\n')
        for line in lines[:5]:  # 처음 5줄만 확인
            line = line.strip()
            if line and len(line) < 50:  # 너무 긴 줄은 제외
                # 한글이나 영문이 포함된 경우
                if re.search(r'[가-힣a-zA-Z]', line):
                    merchant = line
                    break
        
        return {
            "amount": amount,
            "date": date,
            "merchant": merchant,
            "original_text": text
        }


# 싱글톤 인스턴스
_ocr_service = None


def get_ocr_service() -> OCRService:
    """OCR 서비스 인스턴스 반환 (싱글톤)"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


# 전역 함수 (하위 호환성 유지)
async def extract_text_from_image(image_bytes: bytes) -> str:
    """이미지에서 텍스트 추출"""
    service = get_ocr_service()
    return await service.extract_text_from_image(image_bytes)


async def parse_receipt(text: str) -> Dict[str, any]:
    """영수증 파싱"""
    service = get_ocr_service()
    return await service.parse_receipt(text)
