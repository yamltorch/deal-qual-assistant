"""SQL-адаптер репозитория read-model сделок."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.adapters.persistence.mappers import read_model_from_orm, read_model_to_orm
from backend.adapters.persistence.orm_models import ReadModelORM
from backend.domain.entities import DealReadModel
from backend.ports.repositories import ReadModelRepository


class SqlReadModelRepository(ReadModelRepository):
    """Работает с таблицей read-model, обеспечивая идемпотентный апдейт."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, deal_id: str) -> DealReadModel | None:
        """Получить read-model по идентификатору сделки."""

        stmt = select(ReadModelORM).where(ReadModelORM.deal_id == deal_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        return read_model_from_orm(row) if row else None

    def save(self, model: DealReadModel) -> None:
        """Сохранить read-model, обновляя существующую строку."""

        stmt = select(ReadModelORM).where(ReadModelORM.deal_id == model.deal_id)
        existing = self._session.execute(stmt).scalar_one_or_none()
        orm = read_model_to_orm(model, existing)
        if existing is None:
            self._session.add(orm)

    def delete(self, deal_id: str) -> None:
        """Удалить read-model сделки."""

        stmt = delete(ReadModelORM).where(ReadModelORM.deal_id == deal_id)
        self._session.execute(stmt)


