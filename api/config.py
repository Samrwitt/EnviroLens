"""Shared application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://envirolens:envirolens@localhost:5433/envirolens"
    redis_url: str = "redis://localhost:6379/0"
    api_key: str = "dev-api-key-change-me"
    jwt_secret: str = "dev-jwt-secret-change-me"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    dhis2_mock_url: str = "http://localhost:8000/dhis2"
    dhis2_mock_user: str = "admin"
    dhis2_mock_password: str = "district"


@lru_cache
def get_settings() -> Settings:
    return Settings()
