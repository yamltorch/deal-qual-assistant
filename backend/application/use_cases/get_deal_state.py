"""Use case: получить текущее read-model сделки."""

from __future__ import annotations

from dataclasses import dataclass

from backend.domain.entities import DealReadModel
from backend.ports.unit_of_work import UnitOfWorkFactory


@dataclass(frozen=True, slots=True)
class GetDealStateQuery:
    """Запрос на получение read-model по идентификатору сделки."""

    deal_id: str


class GetDealStateHandler:
    """Возвращает сохранённое или пустое состояние сделки."""

    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, query: GetDealStateQuery) -> DealReadModel:
        """Получить read-model, включая пустую заготовку."""

        with self._uow_factory() as uow:
            model = uow.read_models.get(query.deal_id)
        return model or DealReadModel.empty(deal_id=query.deal_id)


