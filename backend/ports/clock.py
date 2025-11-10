"""Порт времени для инжекции детерминированных часов в домен и юзкейсы."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class ClockPort(ABC):
    """Абстракция часов, возвращающих текущее UTC время."""

    @abstractmethod
    def utcnow(self) -> datetime:
        """Получить текущее время в UTC с tzinfo."""


