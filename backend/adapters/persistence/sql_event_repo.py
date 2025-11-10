"""SQL-адаптер репозитория событий сделок."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.adapters.persistence.mappers import event_from_orm, event_to_orm
from backend.adapters.persistence.orm_models import EventORM
from backend.domain.entities import Event
from backend.ports.repositories import EventRepository


class SqlEventRepository(EventRepository):
    """Работает с таблицей событий, используя общий SQLAlchemy Session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event: Event) -> None:
        """Сохранить событие сделки."""

        self._session.add(event_to_orm(event))

    def list_for_deal(self, deal_id: str) -> Sequence[Event]:
        """Вернуть события сделки в порядке создания."""

        stmt = (
            select(EventORM)
            .where(EventORM.deal_id == deal_id)
            .order_by(EventORM.created_at.asc(), EventORM.id.asc())
        )
        rows = self._session.execute(stmt).scalars().all()
        return [event_from_orm(row) for row in rows]

    def delete_for_deal(self, deal_id: str) -> None:
        """Удалить события конкретной сделки."""

        stmt = delete(EventORM).where(EventORM.deal_id == deal_id)
        self._session.execute(stmt)


