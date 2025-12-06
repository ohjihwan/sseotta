# 💰 썼다AI - AI 소비 분석 & 자동 리포트 웹앱

> 사용자의 소비 데이터를 다양한 방식으로 입력받아 AI가 자동으로 카테고리를 분류하고, 소비 패턴을 분석하여 월간 리포트를 생성하는 웹 애플리케이션

---

## 🚀 빠른 실행

### Backend
```bash
cd backend
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
# .env 파일 생성 후 MongoDB URL, JWT_SECRET_KEY 설정
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
python -m http.server 5500
# 또는 VS Code Live Server 사용
```

**접속**: http://localhost:5500 | **API 문서**: http://localhost:8000/docs

---

## 🌟 이 앱으로 사용자는 이렇게 할 수 있습니다

- 📸 **영수증 찍기 → 자동 입력**: 영수증 사진을 업로드하면 OCR로 자동 인식하여 거래 내역이 입력됩니다
- 📝 **텍스트 입력**: "스타벅스 아메리카노 4500원"처럼 자연어로 입력하면 AI가 자동으로 카테고리를 분류합니다
- 📊 **소비 패턴 확인**: 월별, 카테고리별 지출 통계를 한눈에 확인할 수 있습니다
- 📈 **월별 보고서 자동 생성**: AI가 분석한 소비 인사이트와 전월 대비 증감률을 제공합니다
- 🔐 **로그인 후 과거 데이터 영구 확인**: 회원가입 후 모든 거래 내역이 안전하게 저장되어 언제든지 조회 가능합니다
- 📁 **파일 일괄 업로드**: 카드사/은행 거래내역 CSV/Excel 파일을 업로드하면 자동으로 처리됩니다

---

## 📚 프로젝트 개요

### 프로젝트 명칭
**썼다AI** (SSEOTTA AI)

### 프로젝트 목적
사용자의 소비 데이터를 다양한 방식으로 입력받아 AI가 자동으로 카테고리를 분류하고, 소비 패턴을 분석하여 월간 리포트를 생성하는 웹 애플리케이션 개발

### 핵심 가치
- 수동 가계부 작성의 번거로움 제거
- AI 기반 자동 카테고리 분류로 정확성 향상
- 소비 패턴 인사이트 제공으로 재정 관리 개선

---

## 📘 주요 기능

### 1. 데이터 입력 기능

#### 1.1 텍스트 입력
- **설명**: 사용자가 자연어로 소비 내역 입력
- **입력 예시**: "스타벅스 아메리카노 4500원", "2024년 11월 15일 택시비 12000원"
- **처리 과정**: 
  - 날짜, 금액, 상호명 자동 추출
  - AI가 텍스트 분석하여 카테고리 자동 분류
- **검증**: 필수 정보(금액) 누락 시 사용자에게 재입력 요청

#### 1.2 이미지 업로드 (영수증 OCR)
- **설명**: 영수증 사진을 업로드하여 자동 데이터 추출
- **지원 형식**: JPG, PNG, HEIC
- **처리 과정**:
  1. OCR로 영수증 텍스트 추출
  2. 구조화된 데이터로 변환 (날짜, 금액, 항목)
  3. AI가 카테고리 분류
- **예외 처리**: OCR 실패 시 수동 입력 안내

#### 1.3 CSV/Excel 파일 업로드
- **설명**: 카드사/은행 거래내역 파일 일괄 업로드
- **지원 형식**: CSV, XLSX, XLS
- **필수 컬럼**: 날짜, 금액, 거래처(선택)
- **처리 과정**:
  - 파일 파싱 및 데이터 검증
  - 각 거래 건별 AI 카테고리 분류
  - 배치 처리로 대량 데이터 입력

### 2. AI 분석 기능

#### 2.1 자동 카테고리 분류
- **카테고리 목록**:
  - 식비 (외식, 배달, 카페 등)
  - 교통비 (대중교통, 택시, 주유 등)
  - 쇼핑 (의류, 전자제품, 생활용품 등)
  - 문화/여가 (영화, 공연, 취미 등)
  - 의료/건강 (병원, 약국, 헬스 등)
  - 주거/통신 (월세, 관리비, 인터넷 등)
  - 교육 (학원, 서적 등)
  - 기타
- **분류 기준**: 거래처명, 상품명, 금액 패턴 종합 분석
- **정확도 목표**: 90% 이상

#### 2.2 소비 패턴 분석
- **주간 분석**: 요일별 소비 경향
- **월간 분석**: 월별 소비 총액 및 카테고리별 비중
- **비교 분석**: 전월 대비 증감률
- **이상 지출 탐지**: 평소 패턴과 다른 지출 알림

### 3. 리포트 생성 기능

#### 3.1 월간 리포트 자동 생성
- **포함 내용**:
  - 총 소비 금액
  - 카테고리별 지출 금액 및 비율
  - 가장 많이 지출한 카테고리 TOP 3
  - 전월 대비 증감 분석
  - AI가 생성한 소비 인사이트 (예: "이번 달 외식비가 평소보다 30% 증가했습니다")
- **생성 시점**: 매월 1일 자동 생성 또는 사용자 요청 시
- **출력 형식**: 웹 페이지 테이블 + PDF 다운로드(선택)

#### 3.2 데이터 시각화
- **차트 유형**:
  - 파이 차트: 카테고리별 지출 비율
  - 막대 차트: 월별 소비 추이
  - 라인 차트: 일별 지출 누적
- **인터랙션**: 차트 클릭 시 상세 내역 표시

### 4. 사용자 인증 기능

#### 4.1 회원가입
- 이메일, 이름, 비밀번호로 회원가입
- 비밀번호 암호화 저장 (bcrypt)
- 이메일 중복 확인

#### 4.2 로그인
- 이메일/비밀번호 로그인
- JWT 토큰 기반 인증
- 로그인 상태 유지 기능 (localStorage/sessionStorage)

#### 4.3 로그아웃
- 토큰 삭제 및 세션 종료
- 사용자 데이터 보호

---

## ⚙️ 기술 스택

### Frontend
- **언어**: HTML5, CSS3, JavaScript (Vanilla)
- **이유**: 
  - 빠른 프로토타이핑
  - 학습 곡선 낮음
  - 번들링 없이 즉시 실행 가능

### Backend
- **프레임워크**: FastAPI (Python 3.9+)
- **이유**:
  - 빠른 개발 속도
  - 자동 API 문서 생성 (Swagger)
  - 비동기 처리 지원
  - Python AI 라이브러리와 통합 용이

### AI/ML
- **주요 API**: Claude API (Anthropic)
- **OCR**: EasyOCR (한국어/영어 지원)
- **데이터 처리**: Pandas (CSV/Excel 파싱)

### 데이터베이스
- **선택**: MongoDB
- **이유**:
  - 스키마 유연성: AI 분석 결과가 비정형 데이터이므로 구조 변경 용이
  - JSON 네이티브 지원: AI 응답을 그대로 저장 가능
  - 빠른 프로토타이핑: 스키마 설계 없이 바로 시작
  - 별도 설치 불필요: MongoDB Atlas 클라우드 무료 tier 사용 가능
  - 수평 확장성: 데이터 증가 시 샤딩 쉬움
  - 개발 속도: Python과 Motor(비동기) 통합 우수

---

## 📁 프로젝트 구조

```
sseotta-ai/
├─ backend/
│   ├─ app/
│   │   ├─ main.py              # FastAPI 애플리케이션 진입점
│   │   ├─ config.py            # 설정 관리
│   │   ├─ db.py                # MongoDB 연결
│   │   ├─ routers/             # API 라우터
│   │   │   ├─ auth.py          # 인증 (회원가입, 로그인)
│   │   │   ├─ transactions.py  # 거래 내역 CRUD
│   │   │   └─ reports.py       # 리포트 생성
│   │   ├─ models/              # 데이터 모델
│   │   │   ├─ user.py
│   │   │   ├─ transaction.py
│   │   │   └─ report.py
│   │   └─ services/            # 비즈니스 로직
│   │       ├─ base_service.py      # 베이스 서비스 클래스
│   │       ├─ transaction_service.py # 거래 내역 서비스
│   │       ├─ auth_service.py      # JWT 토큰 관리
│   │       ├─ ai_service.py        # Claude API 연동
│   │       ├─ ocr_service.py       # EasyOCR 처리
│   │       └─ file_service.py     # CSV/Excel 파싱
│   └─ requirements.txt
├─ frontend/
│   ├─ index.html               # 메인 HTML
│   ├─ app.js                   # JavaScript 로직
│   └─ styles.css               # 스타일시트
└─ README.md
```

---

## 🗄️ 데이터베이스 스키마 (MongoDB)

### Collections

#### users
```json
{
  "_id": ObjectId,
  "email": String,
  "name": String,
  "hashed_password": String,
  "created_at": DateTime,
  "settings": {
    "default_categories": Array,
    "currency": String
  }
}
```

#### transactions
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "date": DateTime,
  "amount": Number,
  "category": String,
  "sub_category": String (optional),
  "description": String,
  "merchant": String (optional),
  "source_type": Enum["text", "image", "csv"],
  "ai_confidence": Number (0-1),
  "created_at": DateTime,
  "metadata": {
    "original_text": String,
    "ocr_data": Object (if source_type = "image")
  }
}
```

#### monthly_reports
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "month": String ("YYYY-MM"),
  "total_spending": Number,
  "category_breakdown": {
    "식비": { "amount": Number, "percentage": Number, "count": Number },
    "교통비": { "amount": Number, "percentage": Number, "count": Number },
    ...
  },
  "insights": [
    {
      "type": String ("warning" | "info" | "success"),
      "message": String,
      "generated_by": "ai"
    }
  ],
  "comparison": {
    "previous_month_total": Number,
    "change_percentage": Number
  },
  "generated_at": DateTime
}
```

---

## 🔌 API 엔드포인트

**인증**: `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me`  
**거래**: `POST /api/transactions/{text|image|file}`, `GET /api/transactions`, `PUT|DELETE /api/transactions/{id}`  
**리포트**: `GET /api/reports/generate?month=YYYY-MM`, `GET /api/reports/{month}`

자세한 API 문서는 서버 실행 후 http://localhost:8000/docs 에서 확인 가능합니다.

---

## ⚙️ 실행 환경 설정

### 1️⃣ 백엔드 설정

#### 1.1 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 1.2 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

#### 1.3 MongoDB 설정
로컬 MongoDB를 실행하거나 MongoDB Atlas를 사용합니다.
```bash
# 로컬 MongoDB 실행 (설치된 경우)
mongod

# 또는 MongoDB Atlas 사용 시 연결 문자열 사용
```

#### 1.4 환경 변수 설정
`backend` 디렉터리에 `.env` 파일을 생성하고 다음 내용을 설정합니다:
```env
# MongoDB 설정
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=sseotta_ai

# JWT 설정 (프로덕션에서는 반드시 변경!)
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Claude API 설정 (선택사항 - 없으면 규칙 기반 분류 사용)
ANTHROPIC_API_KEY=your-anthropic-api-key

# OCR 설정
EASYOCR_GPU=False

# 서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 1.5 서버 실행
```bash
# backend 디렉터리에서 실행
cd backend

# 개발 모드 (코드 변경 시 자동 재시작)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**접속 주소**:
- API: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- 대체 문서 (ReDoc): http://localhost:8000/redoc

### 2️⃣ 프론트엔드 설정

#### 2.1 로컬 서버 실행
```bash
cd frontend

# Python 내장 서버 사용
python -m http.server 5500

# 또는 VS Code Live Server 확장 사용
# - index.html 우클릭 → "Open with Live Server"
```

**접속 주소**: http://localhost:5500

#### 2.2 API URL 확인
`frontend/app.js` 파일에서 API 기본 URL을 확인하고 필요시 수정합니다:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### 3️⃣ 전체 실행 순서

1. **MongoDB 실행** (로컬 또는 Atlas)
2. **백엔드 서버 실행** (`backend` 디렉터리에서)
3. **프론트엔드 서버 실행** (`frontend` 디렉터리에서)
4. **브라우저에서 접속**: http://localhost:5500

### 4️⃣ 주의사항

- MongoDB가 실행 중이어야 백엔드가 정상 작동합니다
- EasyOCR은 첫 실행 시 모델을 다운로드하므로 시간이 걸릴 수 있습니다
- 프로덕션 환경에서는 반드시 `JWT_SECRET_KEY`를 안전한 값으로 변경하세요
- Claude API 키가 없어도 기본 규칙 기반 분류로 작동합니다

---

## 📦 주요 패키지

**Backend**: FastAPI, Uvicorn, Motor, Pydantic, python-jose, passlib, anthropic, easyocr, pandas, openpyxl  
**Frontend**: Vanilla JavaScript, Fetch API, LocalStorage/SessionStorage

자세한 패키지 목록은 `backend/requirements.txt` 참조

---

## 💡 핵심 개념

### AI 카테고리 분류
Claude API를 활용하여 소비 내역 텍스트를 분석하고 자동으로 카테고리를 분류합니다. API 키가 없는 경우 기본 규칙 기반 분류가 작동합니다. **팩토리 패턴**과 **전략 패턴**을 사용하여 다양한 분류 방식을 지원합니다.

### OCR (Optical Character Recognition)
EasyOCR을 사용하여 영수증 이미지에서 텍스트를 추출합니다. 한국어와 영어를 동시에 지원하며, 첫 실행 시 모델이 자동으로 다운로드됩니다. **싱글톤 패턴**을 사용하여 리소스를 효율적으로 관리합니다.

### JWT 인증
JSON Web Token을 사용하여 사용자 인증을 처리합니다. 로그인 상태 유지 기능을 통해 사용자 편의성을 제공합니다. **캡슐화**를 통해 토큰 관리 로직을 분리했습니다.

### RAG (Retrieval-Augmented Generation)
외부 지식(거래 내역, 소비 패턴)을 검색하여 AI가 더 정확한 인사이트를 생성할 수 있도록 합니다.

### 비동기 처리
FastAPI와 Motor를 활용하여 비동기 처리를 통해 높은 성능을 제공합니다.

### 객체지향 설계 원칙
- **추상화**: BaseService, CategoryClassifier 인터페이스로 공통 기능 추상화
- **캡슐화**: TransactionService, OCRService, AuthManager 클래스로 관련 기능 그룹화
- **다형성**: CategoryClassifier 인터페이스로 Claude/규칙 기반 분류기 교체 가능
- **의존성 주입**: FastAPI Depends를 통한 서비스 인스턴스 주입

### 환경 변수
**필수**: `MONGODB_URL`, `JWT_SECRET_KEY`  
**선택**: `ANTHROPIC_API_KEY` (없으면 규칙 기반 분류 사용), `EASYOCR_GPU` (GPU 사용 시)

**주의사항**: 프로덕션 환경에서는 `JWT_SECRET_KEY`를 반드시 변경하세요. EasyOCR은 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다.

---

## 🚀 개발 로드맵

### Phase 1: MVP (4-6주) ✅
- [x] 텍스트 입력 기능
  → `/backend/app/routers/transactions.py` (`create_transaction_from_text`)
  → `/backend/app/services/transaction_service.py` (`create_transaction`)
  → `/backend/app/services/ai_service.py` (`classify_category`, `extract_transaction_info`)
  → `/frontend/app.js` (`initTextInput`)
  → `/frontend/index.html` (텍스트 입력 폼)

- [x] AI 카테고리 분류
  → `/backend/app/services/ai_service.py` (`CategoryClassifier`, `ClaudeCategoryClassifier`, `RuleBasedCategoryClassifier`)
  → `/backend/app/services/transaction_service.py` (`classify_category`)

- [x] 간단한 월간 리포트
  → `/backend/app/routers/reports.py` (`generate_monthly_report`)
  → `/frontend/app.js` (`initReport`, `renderReport`)

- [x] 기본 테이블 UI
  → `/frontend/index.html` (거래내역 테이블)
  → `/frontend/app.js` (`loadTransactions`, `renderTransactions`, `updateStatistics`)
  → `/frontend/styles.css` (테이블 스타일)

- [x] 사용자 인증 (회원가입, 로그인, 로그아웃)
  → `/backend/app/routers/auth.py` (`signup`, `login`, `get_current_user`)
  → `/backend/app/services/auth_service.py` (`get_password_hash`, `verify_password`, `create_access_token`)
  → `/frontend/app.js` (`initAuth`, `handleLogin`, `handleSignup`, `handleLogout`)
  → `/frontend/utils.js` (`AuthManager`)

- [x] 이미지 OCR 추가 (EasyOCR)
  → `/backend/app/routers/transactions.py` (`create_transaction_from_image`)
  → `/backend/app/services/ocr_service.py` (`OCRService`, `extract_text_from_image`, `parse_receipt`)
  → `/frontend/app.js` (`initImageUpload`)

- [x] CSV/Excel 업로드
  → `/backend/app/routers/transactions.py` (`create_transactions_from_file`)
  → `/backend/app/services/file_service.py` (`parse_csv_file`)
  → `/backend/app/services/transaction_service.py` (`create_transactions_batch`)
  → `/frontend/app.js` (`initFileUpload`)

### Phase 2: 확장 (4-6주)
- [ ] 상세 차트 시각화
- [ ] 데이터 내보내기 (PDF, Excel)
- [ ] 예산 설정 및 알림
- [ ] 모바일 반응형 최적화

### Phase 3: 고도화 (4-8주)
- [ ] 패턴 기반 추천 (예: "이번 달 커피 지출이 많아요")
- [ ] 예산 설정 및 알림
- [ ] 모바일 앱 연동
- [ ] 다국어 지원 (영어)

---

## ⚠️ 위험 요소 및 대응 방안

### 기술적 위험
- **AI 분류 정확도 낮음**: 초기 학습 데이터로 파인튜닝, 사용자 피드백 반영
- **OCR 인식 실패**: 수동 입력 대체 수단 제공
- **대용량 파일 처리**: 배치 처리 및 진행률 표시

### 비즈니스 위험
- **사용자 이탈**: 온보딩 튜토리얼 강화, 샘플 데이터 제공
- **데이터 보안**: 암호화, 정기 백업, GDPR 준수

---

## 📊 성공 지표 (KPI)

- 주간 활성 사용자(WAU): 100명 (3개월 내)
- AI 분류 정확도: 90% 이상
- 평균 거래 입력 시간: 30초 이내
- 사용자 만족도: 4.0/5.0 이상
- 리포트 생성 성공률: 95% 이상

---

## 📝 참고 사항

### 유사 서비스 분석
- **뱅크샐러드**: 자동 연동이 강점이나 수동 입력 불편
- **머니북**: 수동 입력 위주, AI 기능 부족
- **차별점**: AI 기반 자동 분류 + 다양한 입력 방식

### 라이선스
- FastAPI: MIT License
- Claude API: 유료 (사용량 기반)
- MongoDB: SSPL (상용 시 검토 필요)
- EasyOCR: Apache License 2.0

---

## 🔗 참고 자료

### FastAPI
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [FastAPI 튜토리얼](https://fastapi.tiangolo.com/tutorial/)

### MongoDB
- [MongoDB 공식 문서](https://www.mongodb.com/docs/)
- [Motor (비동기 드라이버) 문서](https://motor.readthedocs.io/)

### AI/ML
- [Claude API 문서](https://docs.anthropic.com/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)

### 프론트엔드
- [MDN Web Docs](https://developer.mozilla.org/)
- [JavaScript.info](https://javascript.info/)

---

## 📅 개발 일지

### 2025-12-07
- ✅ 프론트엔드 UI/UX 구현 완료
  - 반응형 디자인 (모바일/태블릿/데스크톱)
  - 텍스트/이미지/파일 입력 기능
  - 거래내역 테이블 및 통계 카드
  - 리포트 섹션
- ✅ 사용자 인증 시스템 구현
  - 회원가입/로그인/로그아웃 기능
  - JWT 토큰 기반 인증
  - 로그인 상태 유지 기능
- ✅ 백엔드 API 구현 완료
  - FastAPI 기반 RESTful API
  - MongoDB 연동
  - 인증 라우터 (회원가입, 로그인)
  - 거래 내역 라우터 (CRUD)
  - 리포트 생성 라우터
- ✅ AI 서비스 통합
  - Claude API 연동 (카테고리 분류)
  - 기본 규칙 기반 분류 (API 키 없을 때)
- ✅ OCR 서비스 구현
  - EasyOCR 적용 (한국어/영어 지원)
  - 영수증 텍스트 추출 및 파싱
- ✅ 파일 처리 기능
  - CSV/Excel 파일 파싱
  - 배치 처리 지원
- ✅ 코드 리팩토링 및 OOP 원칙 적용
  - **추상화**: BaseService, CategoryClassifier 인터페이스 도입
  - **캡슐화**: TransactionService, OCRService, AuthManager 클래스화
  - **다형성**: 팩토리 패턴으로 분류기 교체 가능
  - **의존성 주입**: FastAPI Depends 활용
  - **싱글톤 패턴**: OCR 리더 인스턴스 관리
  - 중복 코드 제거 및 공통 로직 통합

---

## 문서 버전
- **작성일**: 2025-11-17
- **버전**: 1.1
- **작성자**: AI Assistant
- **최종 수정**: 2025-12-07
