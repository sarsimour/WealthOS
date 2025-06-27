from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # API Keys
    AKSHARE_TOKEN: str = ""
    OPENAI_API_KEY: str = ""

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str

    # Server
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    ALLOWED_ORIGINS: List[str] = ["*"]  # Allow all origins for development

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
