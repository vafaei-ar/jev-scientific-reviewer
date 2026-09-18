from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str
    telegram_allowed_user_ids: str = ""

    typesafe_api_key: str
    jev_model: str = "jev-latest"
    jev_endpoint: str = "https://api.typesafe.ai/v1/systemone"
    jev_max_chars: int = 90_000

    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = "https://api.openai.com/v1"

    log_level: str = "INFO"

    @property
    def allowed_user_ids(self) -> set[int]:
        values = [x.strip() for x in self.telegram_allowed_user_ids.split(",") if x.strip()]
        return {int(x) for x in values}

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key and self.llm_model)


@lru_cache
def get_settings() -> Settings:
    return Settings()
