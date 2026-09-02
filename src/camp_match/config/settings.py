from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Camp Match API"
    app_env: str = "local"  # local | test | staging | production
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://jasper:what1234@localhost:5432/camp_match_dev"
    database_pool_size: int = 5
    database_echo: bool = False
    jwt_secret_key: str = "placeholder-key-for-dev-only-change-in-prod"
    jwt_access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
