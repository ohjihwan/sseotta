from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection
from app.routers import auth, transactions, reports
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="썼다AI API",
    description="AI 기반 소비 분석 및 자동 리포트 웹앱 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500", "file://"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행"""
    logger.info("썼다AI 백엔드 서버 시작")
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행"""
    logger.info("썼다AI 백엔드 서버 종료")
    await close_mongo_connection()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "썼다AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}

