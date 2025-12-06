from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB 설정
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "sseotta_ai"
    
    # JWT 설정
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Claude API 설정
    anthropic_api_key: Optional[str] = None
    
    # OCR 설정
    easyocr_gpu: bool = False  # GPU 사용 여부 (CUDA가 설치된 경우 True)
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

