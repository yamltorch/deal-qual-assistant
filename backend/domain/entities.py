"""Доменные сущности для базовой работы с событиями и сделками."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Event:
    """Детерминированное описание события, пришедшего из внешней системы."""

    deal_id: str
    kind: str
    payload: Mapping[str, Any]
    created_at: datetime


@dataclass(frozen=True, slots=True)
class DealReadModel:
    """Компактное представление состояния сделки для отдачи во внешние слои."""

    deal_id: str
    status: str
    score: float | None
    last_event: Mapping[str, Any] | None
    updated_at: datetime | None
    letters: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def empty(cls, deal_id: str) -> "DealReadModel":
        """Вернуть пустую детерминированную заготовку read-model."""

        return cls(
            deal_id=deal_id,
            status="unknown",
            score=None,
            last_event=None,
            updated_at=None,
            letters={},
        )

    def with_event(self, event: Event) -> "DealReadModel":
        """Вернуть новое состояние с учётом последнего события."""

        event_snapshot = {
            "kind": event.kind,
            "payload": dict(event.payload),
            "created_at": event.created_at.isoformat(),
        }
        return DealReadModel(
            deal_id=self.deal_id,
            status="pending",
            score=self.score,
            last_event=event_snapshot,
            updated_at=event.created_at,
            letters=dict(self.letters),
        )


