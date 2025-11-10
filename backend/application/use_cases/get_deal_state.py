"""Use case: получить текущее read-model сделки."""

from __future__ import annotations

from dataclasses import dataclass

from backend.domain.entities import DealReadModel
from backend.ports.repositories import ReadModelRepository


@dataclass(frozen=True, slots=True)
class GetDealStateQuery:
    """Запрос на получение read-model по идентификатору сделки."""

    deal_id: str


class GetDealStateHandler:
    """Возвращает сохранённое или пустое состояние сделки."""

    def __init__(self, read_model_repo: ReadModelRepository) -> None:
        self._read_model_repo = read_model_repo

    def execute(self, query: GetDealStateQuery) -> DealReadModel:
        """Получить read-model, включая пустую заготовку."""

        return self._read_model_repo.get(query.deal_id) or DealReadModel.empty(
            deal_id=query.deal_id,
        )


