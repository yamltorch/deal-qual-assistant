"""Фикстуры pytest для работы с SQL-хранилищем в тестах."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.adapters.persistence.orm_models import Base
from backend.adapters.persistence.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture(scope="function")
def sql_session_factory() -> Iterator[sessionmaker[Session]]:
    """Создаёт sessionmaker поверх in-memory SQLite для быстрых тестов."""

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def sql_uow_factory(
    sql_session_factory: sessionmaker[Session],
) -> Callable[[], SqlAlchemyUnitOfWork]:
    """Возвращает фабрику UnitOfWork, создающую новую сессию на вызов."""

    def _factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(sql_session_factory)

    return _factory


