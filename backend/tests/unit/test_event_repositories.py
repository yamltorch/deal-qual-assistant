"""Проверка CRUD-операций репозиториев событий."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.adapters.persistence.unit_of_work import InMemoryUnitOfWork, SqlAlchemyUnitOfWork
from backend.domain.entities import Event


def _make_event(offset: int = 0, deal_id: str = "deal-1") -> Event:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return Event(
        deal_id=deal_id,
        kind=f"kind-{offset}",
        payload={"value": offset},
        created_at=base + timedelta(minutes=offset),
    )


def test_in_memory_event_repo_crud() -> None:
    uow = InMemoryUnitOfWork()
    with uow:
        event1 = _make_event(1)
        event2 = _make_event(2)
        uow.events.add(event1)
        uow.events.add(event2)
        got = uow.events.list_for_deal("deal-1")
        assert [event.kind for event in got] == ["kind-1", "kind-2"]
        uow.events.delete_for_deal("deal-1")
        assert uow.events.list_for_deal("deal-1") == []


def test_sql_event_repo_crud(sql_uow_factory) -> None:
    event1 = _make_event(1)
    event2 = _make_event(2)
    with sql_uow_factory() as uow:
        assert isinstance(uow, SqlAlchemyUnitOfWork)
        uow.events.add(event1)
        uow.events.add(event2)
        uow.commit()
    with sql_uow_factory() as uow:
        got = uow.events.list_for_deal("deal-1")
        assert [event.kind for event in got] == ["kind-1", "kind-2"]
        uow.events.delete_for_deal("deal-1")
        uow.commit()
    with sql_uow_factory() as uow:
        assert not uow.events.list_for_deal("deal-1")


