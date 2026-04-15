from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Movie API"

    # Optional: simple API-key auth for `/v1/*` routes (X-API-Key header).
    api_key: str | None = None

    # Comma-separated provider names to enable: `mock`, `tmdb`, ...
    providers: str = "mock"

    # TMDb provider settings
    tmdb_api_key: str | None = None
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"


settings = Settings()
