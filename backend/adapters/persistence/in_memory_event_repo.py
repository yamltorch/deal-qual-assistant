"""In-memory адаптер для хранения событий сделок."""

from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Sequence

from backend.domain.entities import Event
from backend.ports.repositories import EventRepository


class InMemoryEventRepository(EventRepository):
    """Хранит события в памяти процесса для целей прототипа."""

    def __init__(self) -> None:
        self._storage: dict[str, list[Event]] = defaultdict(list)
        self._lock = RLock()

    def add(self, event: Event) -> None:
        """Сохранить событие, гарантируя порядок записи."""

        with self._lock:
            self._storage[event.deal_id].append(event)

    def list_for_deal(self, deal_id: str) -> Sequence[Event]:
        """Вернуть список событий сделки."""

        with self._lock:
            return list(self._storage.get(deal_id, []))


