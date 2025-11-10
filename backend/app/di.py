"""Простая DI-обвязка для FastAPI приложения."""

from __future__ import annotations

from functools import lru_cache

from backend.adapters.persistence.in_memory_event_repo import InMemoryEventRepository
from backend.adapters.persistence.in_memory_read_model_repo import (
    InMemoryReadModelRepository,
)
from backend.adapters.time.system_clock import SystemClock
from backend.application.use_cases import (
    GetDealStateHandler,
    IngestEventHandler,
)


class AppContainer:
    """Хранит singleton-объекты приложения без сложной инфраструктуры."""

    def __init__(self) -> None:
        self._event_repo = InMemoryEventRepository()
        self._read_model_repo = InMemoryReadModelRepository()
        self._clock = SystemClock()
        self._ingest_event = IngestEventHandler(
            event_repo=self._event_repo,
            read_model_repo=self._read_model_repo,
            clock=self._clock,
        )
        self._get_state = GetDealStateHandler(read_model_repo=self._read_model_repo)

    @property
    def ingest_event(self) -> IngestEventHandler:
        """Вернуть обработчик приёма события."""

        return self._ingest_event

    @property
    def get_state(self) -> GetDealStateHandler:
        """Вернуть обработчик получения read-model."""

        return self._get_state


@lru_cache(maxsize=1)
def get_container() -> AppContainer:
    """Создать и закешировать контейнер приложения."""

    return AppContainer()


def provide_ingest_event_handler() -> IngestEventHandler:
    """DI-провайдер обработчика приёма события."""

    return get_container().ingest_event


def provide_get_state_handler() -> GetDealStateHandler:
    """DI-провайдер обработчика получения read-model."""

    return get_container().get_state


