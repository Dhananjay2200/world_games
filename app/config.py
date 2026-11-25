"""
Application Configuration Module using Pydantic Settings.
Loads environment variables and provides validated system settings for WorldGames AI.
"""

from functools import lru_cache
from typing import Any, Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "WorldGames AI"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8001

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        """Gracefully handle boolean parsing across varied OS environment flags."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            clean_val = v.strip().lower()
            if clean_val in ("true", "1", "t", "yes", "y", "dev", "development"):
                return True
            if clean_val in ("false", "0", "f", "no", "n", "release", "prod", "production"):
                return False
        return bool(v)

    # NVIDIA NIM / LLM Configuration
    NVIDIA_API_KEY: str = "nvapi-placeholder"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL_NAME: str = "nvidia/nemotron-3.5-bolt-e4b"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    LLM_TIMEOUT: int = 60

    # Research & Search API Configuration
    TAVILY_API_KEY: str = ""
    TAVILY_SEARCH_DEPTH: str = "advanced"

    # Permitted Image Provider Keys (Wikimedia Commons is default free provider)
    UNSPLASH_ACCESS_KEY: str = ""
    PEXELS_API_KEY: str = ""

    # PostgreSQL Database Configuration
    DATABASE_URL: str = "postgresql+psycopg2://postgres:Dk#22000@localhost:5432/world_games_ai"
    DB_POOL_SIZE: int = 15
    DB_MAX_OVERFLOW: int = 30
    DB_ECHO: bool = False

    # Production Limits & Quality Gates
    DAILY_ARTICLE_LIMIT: int = 200
    DEFAULT_QUALITY_THRESHOLD: float = 8.0

    # Admin Portal Authentication
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    JWT_SECRET_KEY: str = "worldgames-super-secret-admin-key-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns a singleton cached instance of application settings."""
    return Settings()
