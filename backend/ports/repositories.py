"""Порты репозиториев для событий и read-model сделок."""

from __future__ import annotations

from typing import Protocol, Sequence

from backend.domain.entities import DealReadModel, Event, Fact


class EventRepository(Protocol):
    """Контракт хранения событий без привязки к конкретной СУБД."""

    def add(self, event: Event) -> None:
        """Сохранить событие для сделки."""

    def list_for_deal(self, deal_id: str) -> Sequence[Event]:
        """Вернуть все события конкретной сделки в порядке записи."""

    def delete_for_deal(self, deal_id: str) -> None:
        """Удалить все события конкретной сделки."""


class FactRepository(Protocol):
    """Контракт хранения фактов, полученных после обработки событий."""

    def upsert(self, fact: Fact) -> None:
        """Идемпотентно сохранить факт, обновив его по ключу сделки и вида."""

    def list_for_deal(self, deal_id: str) -> Sequence[Fact]:
        """Вернуть все факты по идентификатору сделки."""

    def delete_for_deal(self, deal_id: str) -> None:
        """Удалить факты конкретной сделки."""


class ReadModelRepository(Protocol):
    """Контракт доступа к read-model сделок."""

    def get(self, deal_id: str) -> DealReadModel | None:
        """Получить read-model по идентификатору сделки."""

    def save(self, model: DealReadModel) -> None:
        """Сохранить read-model, делая операцию идемпотентной."""

    def delete(self, deal_id: str) -> None:
        """Удалить read-model сделки, если она есть."""


