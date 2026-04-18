from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"

    hotelbeds_api_key: str
    hotelbeds_secret: str
    hotelbeds_env: Literal["test", "production"] = "test"
    hotelbeds_timeout_seconds: int = 10

    aggregator_concurrency_timeout_seconds: int = 15

    @property
    def hotelbeds_base_url(self) -> str:
        if self.hotelbeds_env == "production":
            return "https://api.hotelbeds.com"
        return "https://api.test.hotelbeds.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
