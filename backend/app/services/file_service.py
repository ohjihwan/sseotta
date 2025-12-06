import pandas as pd
from typing import List, Dict, Optional
import logging
from datetime import datetime
import io
import re

logger = logging.getLogger(__name__)


async def parse_csv_file(file_bytes: bytes, filename: str) -> List[Dict[str, any]]:
    """
    CSV 파일을 파싱하여 거래 내역 리스트 반환
    """
    try:
        # 파일 확장자 확인
        if filename.endswith('.csv'):
            # 인코딩 시도 (UTF-8, CP949 등)
            encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
                    break
                except:
                    continue
            
            if df is None:
                raise Exception("CSV 파일을 읽을 수 없습니다. 인코딩을 확인해주세요.")
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise Exception("지원하지 않는 파일 형식입니다.")
        
        transactions = []
        
        # 컬럼명 정규화 (대소문자 무시, 공백 제거)
        df.columns = df.columns.str.strip().str.lower()
        
        # 필수 컬럼 확인
        required_cols = ['date', 'amount', '날짜', '금액']
        date_col = None
        amount_col = None
        desc_col = None
        merchant_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(req in col_lower for req in ['date', '날짜', '거래일']):
                date_col = col
            elif any(req in col_lower for req in ['amount', '금액', '거래금액']):
                amount_col = col
            elif any(req in col_lower for req in ['desc', '설명', '내용', '메모']):
                desc_col = col
            elif any(req in col_lower for req in ['merchant', '거래처', '상호', '가맹점']):
                merchant_col = col
        
        if not date_col or not amount_col:
            raise Exception("필수 컬럼(날짜, 금액)을 찾을 수 없습니다.")
        
        # 데이터 변환
        for _, row in df.iterrows():
            try:
                # 날짜 파싱
                date_value = row[date_col]
                if pd.isna(date_value):
                    continue
                
                if isinstance(date_value, str):
                    date = pd.to_datetime(date_value, errors='coerce')
                else:
                    date = pd.to_datetime(date_value)
                
                if pd.isna(date):
                    date = datetime.now()
                else:
                    date = date.to_pydatetime()
                
                # 금액 파싱
                amount_value = row[amount_col]
                if pd.isna(amount_value):
                    continue
                
                # 문자열인 경우 숫자만 추출
                if isinstance(amount_value, str):
                    amount_str = re.sub(r'[^\d.]', '', amount_value)
                    amount = float(amount_str) if amount_str else None
                else:
                    amount = float(amount_value)
                
                if amount is None or amount <= 0:
                    continue
                
                # 설명 및 거래처
                description = str(row[desc_col]) if desc_col and not pd.isna(row.get(desc_col, None)) else None
                merchant = str(row[merchant_col]) if merchant_col and not pd.isna(row.get(merchant_col, None)) else None
                
                transactions.append({
                    "date": date,
                    "amount": amount,
                    "description": description,
                    "merchant": merchant,
                    "original_text": f"{description or ''} {merchant or ''}".strip()
                })
                
            except Exception as e:
                logger.warning(f"행 파싱 오류: {e}")
                continue
        
        return transactions
        
    except Exception as e:
        logger.error(f"파일 파싱 오류: {e}")
        raise Exception(f"파일을 처리하는 중 오류가 발생했습니다: {str(e)}")

