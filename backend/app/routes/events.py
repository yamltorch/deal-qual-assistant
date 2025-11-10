"""Маршруты работы с событиями сделок."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.app.di import provide_ingest_event_handler
from backend.application.use_cases import (
    IngestEventCommand,
    IngestEventHandler,
)
from backend.schemas.events import EventIn
from backend.schemas.read_model import DealStateOut

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "",
    response_model=DealStateOut,
    status_code=status.HTTP_201_CREATED,
)
def post_event(
    payload: EventIn,
    handler: IngestEventHandler = Depends(provide_ingest_event_handler),
) -> DealStateOut:
    """Принять событие и вернуть обновлённое состояние сделки."""

    result = handler.execute(
        IngestEventCommand(
            deal_id=payload.deal_id,
            kind=payload.kind,
            payload=payload.payload,
        )
    )
    return DealStateOut.from_domain(result)


