"""Pydantic-схемы для read-model сделок."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.domain.entities import DealReadModel


class DealStateOut(BaseModel):
    """Выходная схема read-model для API и UI."""

    model_config = ConfigDict(from_attributes=True)

    deal_id: str = Field(..., description="Идентификатор сделки")
    status: str = Field(..., description="Текущий статус сделки")
    score: float | None = Field(
        default=None,
        description="Текущая оценка качества сделки",
    )
    last_event: dict[str, Any] | None = Field(
        default=None,
        description="Последнее событие, учтённое в состоянии",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Момент последнего обновления read-model",
    )
    letters: dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительные агрегаты по буквам MED2IC3",
    )

    @classmethod
    def from_domain(cls, model: DealReadModel) -> "DealStateOut":
        """Сконвертировать доменную read-model в DTO."""

        return cls.model_validate(model, from_attributes=True)


