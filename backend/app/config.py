"""Settings loaded from the environment (and backend/.env if present)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # No default on purpose: a missing DATABASE_URL should fail loudly rather
    # than silently falling back to SQLite, which would diverge from Postgres
    # on enums, JSON and case sensitivity.
    DATABASE_URL: str
    SQL_ECHO: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
