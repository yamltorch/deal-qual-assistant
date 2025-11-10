"""Use case: принять событие и обновить read-model сделки."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.domain.entities import DealReadModel, Event
from backend.ports.clock import ClockPort
from backend.ports.repositories import EventRepository, ReadModelRepository


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
        event_repo: EventRepository,
        read_model_repo: ReadModelRepository,
        clock: ClockPort,
    ) -> None:
        self._event_repo = event_repo
        self._read_model_repo = read_model_repo
        self._clock = clock

    def execute(self, command: IngestEventCommand) -> DealReadModel:
        """Сохранить событие и вернуть обновлённое состояние сделки."""

        event = Event(
            deal_id=command.deal_id,
            kind=command.kind,
            payload=dict(command.payload),
            created_at=self._clock.utcnow(),
        )
        self._event_repo.add(event)
        current = self._read_model_repo.get(command.deal_id) or DealReadModel.empty(
            deal_id=command.deal_id,
        )
        updated = current.with_event(event)
        self._read_model_repo.save(updated)
        return updated


