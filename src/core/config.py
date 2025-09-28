from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Nexus RAG API"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Vector Store
    VECTOR_STORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Object Storage (Cloudflare R2)
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None
    R2_PUBLIC_BASE_URL: Optional[str] = None
    R2_ENDPOINT_URL: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()