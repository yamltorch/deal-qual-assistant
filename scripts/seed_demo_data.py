"""Заполнить базу демо-данными для UI."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.adapters.persistence.orm_models import Base
from backend.adapters.persistence.unit_of_work import SqlAlchemyUnitOfWork
from backend.config.settings import get_settings
from backend.domain.entities import DealReadModel


def seed_demo_deal() -> None:
    """Создать read-model демо-сделки, чтобы UI показывал состояние."""

    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
    if settings.create_schema:
        Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        read_model = DealReadModel(
            deal_id="demo-deal",
            status="pending",
            score=0.65,
            last_event={
                "kind": "seeded",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            updated_at=datetime.now(timezone.utc),
            letters={
                "B": {"score": 0.6, "status": "progress"},
                "A": {"score": 0.5, "status": "progress"},
            },
        )
        uow.read_models.save(read_model)
        uow.commit()


if __name__ == "__main__":
    seed_demo_deal()

