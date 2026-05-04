"""
backend/core/config.py
Configuración central con pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pass@localhost:5432/andamiaje"

    # Auth
    JWT_SECRET_KEY: str = "cambia-esto-en-produccion-minimo-32-chars!!"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@andamiaje.com"
    SENDGRID_FROM_NAME: str = "Andamiaje Python"

    # URLs
    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:8501"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
