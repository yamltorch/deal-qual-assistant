"""Маршрут проверки живости сервиса."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def read_health() -> dict[str, bool]:
    """Вернуть признак работоспособности сервиса."""

    return {"ok": True}


