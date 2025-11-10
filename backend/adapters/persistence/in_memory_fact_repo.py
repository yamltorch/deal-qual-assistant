"""In-memory адаптер хранения фактов сделок."""

from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Sequence

from backend.domain.entities import Fact
from backend.ports.repositories import FactRepository


class InMemoryFactRepository(FactRepository):
    """Хранит факты в памяти процесса с идемпотентным upsert."""

    def __init__(self) -> None:
        self._storage: dict[str, dict[str, Fact]] = defaultdict(dict)
        self._lock = RLock()

    def upsert(self, fact: Fact) -> None:
        """Сохранить или обновить факт сделки."""

        with self._lock:
            self._storage[fact.deal_id][fact.kind] = fact

    def list_for_deal(self, deal_id: str) -> Sequence[Fact]:
        """Вернуть список фактов для сделки."""

        with self._lock:
            return list(self._storage.get(deal_id, {}).values())

    def delete_for_deal(self, deal_id: str) -> None:
        """Удалить факты сделки."""

        with self._lock:
            self._storage.pop(deal_id, None)


