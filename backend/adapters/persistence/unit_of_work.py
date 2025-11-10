"""Реализации UnitOfWork для SQL и in-memory вариантов хранилища."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from backend.adapters.persistence.in_memory_event_repo import InMemoryEventRepository
from backend.adapters.persistence.in_memory_fact_repo import InMemoryFactRepository
from backend.adapters.persistence.in_memory_read_model_repo import InMemoryReadModelRepository
from backend.adapters.persistence.sql_event_repo import SqlEventRepository
from backend.adapters.persistence.sql_fact_repo import SqlFactRepository
from backend.adapters.persistence.sql_read_model_repo import SqlReadModelRepository
from backend.ports.repositories import EventRepository, FactRepository, ReadModelRepository
from backend.ports.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """UnitOfWork на базе SQLAlchemy: один Session на юзкейс."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Optional[Session] = None
        self._events: Optional[EventRepository] = None
        self._facts: Optional[FactRepository] = None
        self._read_models: Optional[ReadModelRepository] = None
        self._committed = False

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._events = SqlEventRepository(self._session)
        self._facts = SqlFactRepository(self._session)
        self._read_models = SqlReadModelRepository(self._session)
        self._committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self._session:
            return
        try:
            if exc_type is not None:
                self._session.rollback()
            elif not self._committed:
                self._session.commit()
        finally:
            self._session.close()
            self._session = None
            self._events = None
            self._facts = None
            self._read_models = None
            self._committed = False

    @property
    def events(self) -> EventRepository:
        """Вернуть репозиторий событий."""

        if self._events is None:
            raise RuntimeError("UnitOfWork не открыт через контекстный менеджер.")
        return self._events

    @property
    def facts(self) -> FactRepository:
        """Вернуть репозиторий фактов."""

        if self._facts is None:
            raise RuntimeError("UnitOfWork не открыт через контекстный менеджер.")
        return self._facts

    @property
    def read_models(self) -> ReadModelRepository:
        """Вернуть репозиторий read-model."""

        if self._read_models is None:
            raise RuntimeError("UnitOfWork не открыт через контекстный менеджер.")
        return self._read_models

    def commit(self) -> None:
        """Зафиксировать изменения."""

        if not self._session:
            raise RuntimeError("Нельзя вызвать commit до открытия UnitOfWork.")
        self._session.commit()
        self._committed = True

    def rollback(self) -> None:
        """Откатить изменения."""

        if self._session:
            self._session.rollback()


class InMemoryUnitOfWork(UnitOfWork):
    """UnitOfWork, объединяющий in-memory реализации репозиториев."""

    def __init__(
        self,
        event_repo: InMemoryEventRepository | None = None,
        fact_repo: InMemoryFactRepository | None = None,
        read_model_repo: InMemoryReadModelRepository | None = None,
    ) -> None:
        self._event_repo = event_repo or InMemoryEventRepository()
        self._fact_repo = fact_repo or InMemoryFactRepository()
        self._read_model_repo = read_model_repo or InMemoryReadModelRepository()

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    @property
    def events(self) -> EventRepository:
        return self._event_repo

    @property
    def facts(self) -> FactRepository:
        return self._fact_repo

    @property
    def read_models(self) -> ReadModelRepository:
        return self._read_model_repo

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None


