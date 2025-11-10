"""Порты репозиториев для событий и read-model сделок."""

from __future__ import annotations

from typing import Protocol, Sequence

from backend.domain.entities import DealReadModel, Event


class EventRepository(Protocol):
    """Контракт хранения событий без привязки к конкретной СУБД."""

    def add(self, event: Event) -> None:
        """Сохранить событие для сделки."""

    def list_for_deal(self, deal_id: str) -> Sequence[Event]:
        """Вернуть все события конкретной сделки в порядке записи."""


class ReadModelRepository(Protocol):
    """Контракт доступа к read-model сделок."""

    def get(self, deal_id: str) -> DealReadModel | None:
        """Получить read-model по идентификатору сделки."""

    def save(self, model: DealReadModel) -> None:
        """Сохранить read-model, делая операцию идемпотентной."""


