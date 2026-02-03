from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API config
    api_key: str = "dev-key-change-me"
    api_title: str = "Star Wars API"
    api_version: str = "1.0.0"

    # SWAPI config
    swapi_base_url: str = "https://swapi.dev/api"
    swapi_timeout: float = 10.0
    swapi_max_retries: int = 3

    # Cache config (in-memory for now)
    # TODO: migrate to Redis for production multi-instance deployment
    cache_ttl_seconds: int = 300

    # Rate limiting - SWAPI has 10k/day limit, we'll be conservative
    rate_limit_requests_per_second: float = 5.0

    # Logging
    log_level: str = "INFO"

    # CORS - adjust for production
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5175", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
