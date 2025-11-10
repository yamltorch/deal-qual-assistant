"""Простая DI-обвязка для FastAPI приложения."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.adapters.time.system_clock import SystemClock
from backend.adapters.persistence.orm_models import Base
from backend.adapters.persistence.unit_of_work import SqlAlchemyUnitOfWork
from backend.application.use_cases import (
    GetDealStateHandler,
    IngestEventHandler,
)
from backend.config.settings import get_settings
from backend.ports.unit_of_work import UnitOfWorkFactory


class AppContainer:
    """Хранит singleton-объекты приложения без сложной инфраструктуры."""

    def __init__(self) -> None:
        settings = get_settings()
        engine = create_engine(
            settings.database_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
        )
        if settings.create_schema:
            Base.metadata.create_all(engine)
        session_factory = sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self._uow_factory: UnitOfWorkFactory = lambda: SqlAlchemyUnitOfWork(session_factory)
        self._clock = SystemClock()
        self._ingest_event = IngestEventHandler(
            uow_factory=self._uow_factory,
            clock=self._clock,
        )
        self._get_state = GetDealStateHandler(uow_factory=self._uow_factory)

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


