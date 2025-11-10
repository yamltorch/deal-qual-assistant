"""Pydantic-схемы для работы с событиями API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventIn(BaseModel):
    """Входная схема события из внешнего API."""

    model_config = ConfigDict(str_strip_whitespace=True)

    deal_id: str = Field(..., description="Идентификатор сделки")
    kind: str = Field(..., description="Тип события")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Произвольное содержимое события",
    )


