"""Use case: принять событие и обновить read-model сделки."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.domain.entities import DealReadModel, Event
from backend.ports.clock import ClockPort
from backend.ports.unit_of_work import UnitOfWorkFactory


@dataclass(frozen=True, slots=True)
class IngestEventCommand:
    """Команда на приём события от внешнего источника."""

    deal_id: str
    kind: str
    payload: Mapping[str, Any]


class IngestEventHandler:
    """Детерминированно записывает событие и обновляет read-model."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        clock: ClockPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: IngestEventCommand) -> DealReadModel:
        """Сохранить событие и вернуть обновлённое состояние сделки."""

        event = Event(
            deal_id=command.deal_id,
            kind=command.kind,
            payload=dict(command.payload),
            created_at=self._clock.utcnow(),
        )
        with self._uow_factory() as uow:
            uow.events.add(event)
            current = uow.read_models.get(command.deal_id) or DealReadModel.empty(
                deal_id=command.deal_id,
            )
            updated = current.with_event(event)
            uow.read_models.save(updated)
            uow.commit()
            return updated


