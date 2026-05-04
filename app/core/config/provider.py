from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class ConfigSettings(BaseSettings):
    # GitHub App credentials
    GITHUB_APP_ID: str = Field(default="", env="GITHUB_APP_ID")
    GITHUB_PRIVATE_KEY_PATH: str = Field(default="", env="GITHUB_PRIVATE_KEY_PATH")
    GITHUB_WEBHOOK_SECRET: str = Field(default="", env="GITHUB_WEBHOOK_SECRET")

    # LLM configuration
    DEFAULT_LLM_PROVIDER: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_BASE_MODEL: str = Field(default="", env="OPENAI_BASE_MODEL")

    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_BASE_MODEL: str = Field(default="", env="GEMINI_BASE_MODEL")

    # App constants
    GITHUB_API: str = Field(default="", env="GITHUB_API")
    INTERNAL_API: str = Field(default="", env="INTERNAL_API")
    CELERY_BROKER_URL: str = Field(default="", env="CELERY_BROKER_URL")
    CELERY_BACKEND_URL: str = Field(default="", env="CELERY_BACKEND_URL")
    REDIS_BACKEND_URL: str = Field(default="", env="REDIS_BACKEND_URL")

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_config():
    return ConfigSettings()
