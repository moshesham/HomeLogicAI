from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str = "sqlite:///./data/homelogicai.db"
    storage_path: str = "./data/projects"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    scraper_service_url: str = "http://scraper:8001"
    scrape_cache_ttl: int = 86400
    max_compare_products: int = 4
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
