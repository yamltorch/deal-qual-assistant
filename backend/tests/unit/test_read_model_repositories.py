"""Проверка CRUD-операций репозиториев read-model."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.adapters.persistence.unit_of_work import InMemoryUnitOfWork
from backend.domain.entities import DealReadModel


def _make_read_model(status: str = "pending") -> DealReadModel:
    return DealReadModel(
        deal_id="deal-1",
        status=status,
        score=0.87,
        last_event={"kind": "ingested"},
        updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        letters={"B": {"score": 0.7}},
    )


def test_in_memory_read_model_repo_crud() -> None:
    uow = InMemoryUnitOfWork()
    with uow:
        empty = DealReadModel.empty("deal-1")
        uow.read_models.save(empty)
        stored = uow.read_models.get("deal-1")
        assert stored == empty
        updated = _make_read_model(status="go")
        uow.read_models.save(updated)
        persisted = uow.read_models.get("deal-1")
        assert persisted.status == "go"
        uow.read_models.delete("deal-1")
        assert uow.read_models.get("deal-1") is None


def test_sql_read_model_repo_crud(sql_uow_factory) -> None:
    with sql_uow_factory() as uow:
        uow.read_models.save(DealReadModel.empty("deal-1"))
        uow.commit()
    with sql_uow_factory() as uow:
        uow.read_models.save(_make_read_model(status="go"))
        uow.commit()
    with sql_uow_factory() as uow:
        stored = uow.read_models.get("deal-1")
        assert stored is not None
        assert stored.status == "go"
        assert stored.letters["B"]["score"] == pytest.approx(0.7)
        assert stored.score == pytest.approx(0.87)
        uow.read_models.delete("deal-1")
        uow.commit()
    with sql_uow_factory() as uow:
        assert uow.read_models.get("deal-1") is None


