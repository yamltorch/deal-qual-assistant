"""Мапперы ORM ↔ dataclass для слоя хранения данных."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from backend.adapters.persistence.orm_models import EventORM, FactORM, ReadModelORM
from backend.domain.entities import DealReadModel, Event, Fact


def _normalize_dt(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _to_float(value: float | Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def event_to_orm(event: Event) -> EventORM:
    """Сконвертировать доменное событие в ORM-модель."""

    return EventORM(
        deal_id=event.deal_id,
        kind=event.kind,
        payload=dict(event.payload),
        created_at=_normalize_dt(event.created_at),
    )


def event_from_orm(model: EventORM) -> Event:
    """Сконвертировать ORM-событие в доменный объект."""

    return Event(
        deal_id=model.deal_id,
        kind=model.kind,
        payload=dict(model.payload),
        created_at=_normalize_dt(model.created_at),
    )


def fact_to_orm(fact: Fact, target: FactORM | None = None) -> FactORM:
    """Сконвертировать факт в ORM, переиспользуя экземпляр, если он задан."""

    if target is None:
        return FactORM(
            deal_id=fact.deal_id,
            kind=fact.kind,
            payload=dict(fact.payload),
            confidence=fact.confidence,
            observed_at=_normalize_dt(fact.observed_at),
            source=fact.source,
        )
    target.payload = dict(fact.payload)
    target.confidence = fact.confidence
    target.observed_at = _normalize_dt(fact.observed_at)
    target.source = fact.source
    return target


def fact_from_orm(model: FactORM) -> Fact:
    """Сконвертировать ORM-факт в доменный объект."""

    return Fact(
        deal_id=model.deal_id,
        kind=model.kind,
        payload=dict(model.payload),
        confidence=_to_float(model.confidence),
        observed_at=_normalize_dt(model.observed_at),
        source=model.source,
    )


def read_model_to_orm(
    model: DealReadModel,
    target: ReadModelORM | None = None,
) -> ReadModelORM:
    """Сконвертировать read-model в ORM-модель."""

    if target is None:
        return ReadModelORM(
            deal_id=model.deal_id,
            status=model.status,
            score=model.score,
            last_event=dict(model.last_event) if model.last_event else None,
            updated_at=_normalize_dt(model.updated_at),
            letters=dict(model.letters),
        )
    target.status = model.status
    target.score = model.score
    target.last_event = dict(model.last_event) if model.last_event else None
    target.updated_at = _normalize_dt(model.updated_at)
    target.letters = dict(model.letters)
    return target


def read_model_from_orm(model: ReadModelORM) -> DealReadModel:
    """Сконвертировать ORM read-model в доменный dataclass."""

    return DealReadModel(
        deal_id=model.deal_id,
        status=model.status,
        score=_to_float(model.score),
        last_event=dict(model.last_event) if model.last_event else None,
        updated_at=_normalize_dt(model.updated_at),
        letters=dict(model.letters or {}),
    )


