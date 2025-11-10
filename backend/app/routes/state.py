"""Маршруты для чтения состояния сделки."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.di import provide_get_state_handler
from backend.application.use_cases import (
    GetDealStateHandler,
    GetDealStateQuery,
)
from backend.schemas.read_model import DealStateOut

router = APIRouter(prefix="/state", tags=["state"])


@router.get("/{deal_id}", response_model=DealStateOut)
def read_state(
    deal_id: str,
    handler: GetDealStateHandler = Depends(provide_get_state_handler),
) -> DealStateOut:
    """Вернуть read-model сделки по идентификатору."""

    result = handler.execute(GetDealStateQuery(deal_id=deal_id))
    return DealStateOut.from_domain(result)


