from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# MongoDB 클라이언트
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """MongoDB 연결"""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.mongodb_db_name]
        # 연결 테스트
        await client.admin.command('ping')
        logger.info("MongoDB 연결 성공")
    except Exception as e:
        logger.error(f"MongoDB 연결 실패: {e}")
        raise


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    global client
    if client:
        client.close()
        logger.info("MongoDB 연결 종료")


def get_database():
    """데이터베이스 인스턴스 반환"""
    return database

