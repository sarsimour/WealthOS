from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # API Keys
    AKSHARE_TOKEN: str = ""
    OPENAI_API_KEY: str = ""
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # LangSmith Configuration
    LANGSMITH_API_KEY: str = "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"
    LANGSMITH_PROJECT: str = "WealthOS"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_TRACING: bool = True

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
