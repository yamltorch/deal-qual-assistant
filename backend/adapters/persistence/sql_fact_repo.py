"""SQL-адаптер репозитория фактов сделок."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.adapters.persistence.mappers import fact_from_orm, fact_to_orm
from backend.adapters.persistence.orm_models import FactORM
from backend.domain.entities import Fact
from backend.ports.repositories import FactRepository


class SqlFactRepository(FactRepository):
    """Хранит факты в таблице PostgreSQL, обеспечивая идемпотентный upsert."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, fact: Fact) -> None:
        """Сохранить факт, обновив запись по deal_id и kind."""

        stmt = select(FactORM).where(
            FactORM.deal_id == fact.deal_id,
            FactORM.kind == fact.kind,
        )
        existing = self._session.execute(stmt).scalar_one_or_none()
        orm = fact_to_orm(fact, existing)
        if existing is None:
            self._session.add(orm)

    def list_for_deal(self, deal_id: str) -> Sequence[Fact]:
        """Вернуть факты конкретной сделки."""

        stmt = (
            select(FactORM)
            .where(FactORM.deal_id == deal_id)
            .order_by(FactORM.observed_at.desc(), FactORM.id.desc())
        )
        rows = self._session.execute(stmt).scalars().all()
        return [fact_from_orm(row) for row in rows]

    def delete_for_deal(self, deal_id: str) -> None:
        """Удалить факты сделки."""

        stmt = delete(FactORM).where(FactORM.deal_id == deal_id)
        self._session.execute(stmt)


