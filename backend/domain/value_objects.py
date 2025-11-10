"""Value-объекты доменного слоя для пересчёта сделок."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class FrameworkCompleteness:
    """Агрегированная полнота по конкретному фреймворку."""

    framework_id: str
    per_letter: Mapping[str, float]
    yes_counts: Mapping[str, int]
    score: float


@dataclass(frozen=True, slots=True)
class GateDecision:
    """Результат применения ворот для фреймворка."""

    framework_id: str
    status: str
    checks: Mapping[str, bool]
