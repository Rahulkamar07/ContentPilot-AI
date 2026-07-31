from typing import List, Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General App Configuration
    PROJECT_NAME: str = "ContentPilot AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = "development"
    DEBUG: bool = False
    GIT_COMMIT: Optional[str] = "dev-commit"

    # API Prefix & Security
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(
        default="super-secret-jwt-signing-key-minimum-32-characters-long",
        description="JWT secret signing key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # 30 days

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://contentpilot_user:SecureDbPassword123!@localhost:5432/contentpilot_db",
        description="Async PostgreSQL Database URL"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Cache & Broker
    REDIS_URL: str = Field(
        default="redis://:SecureRedisPassword123!@localhost:6379/0",
        description="Redis connection URL"
    )

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # External Provider Keys (Optional for Sprint 1 foundation)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None


settings = Settings()
