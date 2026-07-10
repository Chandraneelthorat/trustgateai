from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+psycopg://trustgateai:trustgateai@localhost:5432/trustgateai"
    )
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    skip_celery_sync: bool = False
    openapi_url: str = "/openapi.json"

    # Comma-separated allowlist of browser origins permitted to call the API.
    # Use "*" (default) to allow any origin — fine for local dev, but set explicit
    # origins (e.g. your Vercel URL) in production.
    cors_origins: str = "*"

    # Release-gate thresholds on the 0–100 composite risk score. A run fails at or
    # above fail, warns at or above warn (or on medium/high findings).
    policy_fail_threshold: float = 67.0
    policy_warn_threshold: float = 34.0

    # API-key auth. Off by default so local/demo usage stays open. When true, every
    # non-health endpoint requires a valid key (X-API-Key or Authorization: Bearer).
    # admin_api_key is a bootstrap master key used to mint/manage keys via /auth/keys.
    require_api_key: bool = False
    admin_api_key: str | None = None

    @property
    def database_url_sync(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.cors_origins or "").strip()
        if raw in ("", "*"):
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
