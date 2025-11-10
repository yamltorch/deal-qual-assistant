"""Проверка CRUD-операций репозиториев фактов."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.adapters.persistence.unit_of_work import InMemoryUnitOfWork
from backend.domain.entities import Fact


def _make_fact(
    observed_offset: int,
    confidence: float | None = 0.5,
    deal_id: str = "deal-1",
    kind: str = "fact-kind",
) -> Fact:
    observed_at = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=observed_offset)
    return Fact(
        deal_id=deal_id,
        kind=kind,
        payload={"observed": observed_offset},
        confidence=confidence,
        observed_at=observed_at,
        source="extractor",
    )


def test_in_memory_fact_repo_crud() -> None:
    uow = InMemoryUnitOfWork()
    with uow:
        initial = _make_fact(0, confidence=0.4)
        updated = _make_fact(5, confidence=0.9)
        uow.facts.upsert(initial)
        uow.facts.upsert(updated)
        stored = uow.facts.list_for_deal("deal-1")
        assert len(stored) == 1
        assert stored[0].confidence == 0.9
        uow.facts.delete_for_deal("deal-1")
        assert uow.facts.list_for_deal("deal-1") == []


def test_sql_fact_repo_crud(sql_uow_factory) -> None:
    initial = _make_fact(0, confidence=0.4)
    updated = _make_fact(5, confidence=0.9)
    with sql_uow_factory() as uow:
        uow.facts.upsert(initial)
        uow.commit()
    with sql_uow_factory() as uow:
        uow.facts.upsert(updated)
        uow.commit()
    with sql_uow_factory() as uow:
        stored = uow.facts.list_for_deal("deal-1")
        assert len(stored) == 1
        assert stored[0].confidence == 0.9
        assert stored[0].payload["observed"] == 5
        uow.facts.delete_for_deal("deal-1")
        uow.commit()
    with sql_uow_factory() as uow:
        assert uow.facts.list_for_deal("deal-1") == []


