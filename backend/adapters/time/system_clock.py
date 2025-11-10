"""Системная реализация порта ClockPort."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.ports.clock import ClockPort


class SystemClock(ClockPort):
    """Возвращает текущее UTC время операционной системы."""

    def utcnow(self) -> datetime:
        """Получить текущее время в UTC."""

        return datetime.now(timezone.utc)


