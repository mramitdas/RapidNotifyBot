"""Application settings loaded from environment (.env).

See .env.example for documentation of every value. Never commit .env.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "postgresql+asyncpg://rapid:rapid@localhost:5432/rapidnotify"
    bot_token: str = "changeme"
    key_pepper: str = "changeme-32-byte-min-random-string"

    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    max_payload_bytes: int = 8192

    rate_limit_tiers: dict[str, tuple[int, int]] = {"standard": (60, 60)}

    log_level: str = "INFO"

    # External base URL used in bot messages (channel page link)
    public_base_url: str = "http://localhost:8000"

    def rate_limit_tuples(self) -> tuple[int, int]:
        return self.rate_limit_requests, self.rate_limit_window_seconds

    def rate_limit_for(self, tier: str) -> tuple[int, int]:
        limits = self.rate_limit_tiers
        if tier in limits:
            return limits[tier]
        return self.rate_limit_tuples()


@lru_cache
def get_settings() -> Settings:
    return Settings()
