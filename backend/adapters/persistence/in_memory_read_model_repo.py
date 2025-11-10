"""In-memory адаптер для хранения read-model сделок."""

from __future__ import annotations

from threading import RLock

from backend.domain.entities import DealReadModel
from backend.ports.repositories import ReadModelRepository


class InMemoryReadModelRepository(ReadModelRepository):
    """Хранит read-model целиком в памяти процесса."""

    def __init__(self) -> None:
        self._storage: dict[str, DealReadModel] = {}
        self._lock = RLock()

    def get(self, deal_id: str) -> DealReadModel | None:
        """Вернуть read-model сделки или None."""

        with self._lock:
            return self._storage.get(deal_id)

    def save(self, model: DealReadModel) -> None:
        """Идемпотентно сохранить read-model."""

        with self._lock:
            self._storage[model.deal_id] = model

    def delete(self, deal_id: str) -> None:
        """Удалить read-model сделки."""

        with self._lock:
            self._storage.pop(deal_id, None)


