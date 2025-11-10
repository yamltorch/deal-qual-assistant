"""Настройки приложения: соединение с БД и сервисные флаги."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Инкапсулирует конфигурацию backend-приложения."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(
        default="postgresql+psycopg://deal:deal@postgres:5432/deal_qual",
        alias="DATABASE_URL",
        description="Строка подключения к PostgreSQL.",
    )
    create_schema: bool = Field(
        default=True,
        alias="DB_CREATE_SCHEMA",
        description="Создавать ли таблицы автоматически при старте.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Вернуть кэшированный экземпляр настроек."""

    return Settings()

