"""Порт UnitOfWork обеспечивает транзакционную работу репозиториев."""

from __future__ import annotations

from typing import Callable, Protocol, TypeVar

from backend.ports.repositories import EventRepository, FactRepository, ReadModelRepository

TUnitOfWork = TypeVar("TUnitOfWork", bound="UnitOfWork")


class UnitOfWork(Protocol):
    """Инкапсулирует транзакцию: одна Session и один commit на юзкейс."""

    @property
    def events(self) -> EventRepository:
        """Вернуть репозиторий событий на текущей сессии."""

    @property
    def facts(self) -> FactRepository:
        """Вернуть репозиторий фактов на текущей сессии."""

    @property
    def read_models(self) -> ReadModelRepository:
        """Вернуть репозиторий read-model на текущей сессии."""

    def commit(self) -> None:
        """Зафиксировать изменения в хранилище."""

    def rollback(self) -> None:
        """Откатить изменения, если юзкейс завершился с ошибкой."""

    def __enter__(self: TUnitOfWork) -> TUnitOfWork:
        """Начать контекст UnitOfWork."""

    def __exit__(self, exc_type, exc, tb) -> None:
        """Завершить контекст, откатив изменения при ошибке."""


UnitOfWorkFactory = Callable[[], UnitOfWork]


