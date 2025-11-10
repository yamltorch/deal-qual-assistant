"""Доменные правила пересчёта по фреймворкам BANT и MED2IC3."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from backend.config.frameworks import FrameworkConfig
from backend.domain.entities import Fact
from backend.domain.value_objects import FrameworkCompleteness, GateDecision


def resolve_conflicts(facts: Sequence[Fact]) -> dict[str, Fact]:
    """Выбрать по одному факту каждого вида по уверености и свежести."""

    resolved: dict[str, Fact] = {}
    for fact in facts:
        current = resolved.get(fact.kind)
        if current is None or _is_better_fact(fact, current):
            resolved[fact.kind] = fact
    return resolved


def calc_completeness(
    resolved: Mapping[str, Fact],
    framework: FrameworkConfig,
) -> FrameworkCompleteness:
    """Посчитать полноту по буквам и общий скор для фреймворка."""

    per_letter: dict[str, float] = {}
    yes_counts: dict[str, int] = {}
    total_weight = sum(letter.weight for letter in framework.letters)
    weighted_sum = 0.0
    for letter in framework.letters:
        fact = resolved.get(letter.fact_kind)
        yes_count = _count_yes(fact, letter.checklist)
        completeness = _discretize_yes(yes_count)
        per_letter[letter.key] = completeness
        yes_counts[letter.key] = yes_count
        weighted_sum += completeness * letter.weight
    score = weighted_sum / total_weight if total_weight else 0.0
    return FrameworkCompleteness(
        framework_id=framework.id,
        per_letter=per_letter,
        yes_counts=yes_counts,
        score=round(score, 4),
    )


def apply_gates(
    completeness: FrameworkCompleteness,
    framework: FrameworkConfig,
) -> GateDecision:
    """Определить статус сделки по воротам фреймворка."""

    last_decision: GateDecision | None = None
    for gate in framework.gates:
        checks: dict[str, bool] = {}
        if gate.min_score is not None:
            checks["score"] = completeness.score >= gate.min_score
        for letter, threshold in gate.required_letters:
            checks[letter] = completeness.per_letter.get(letter, 0.0) >= threshold
        decision = GateDecision(
            framework_id=framework.id,
            status=gate.status,
            checks=checks,
        )
        if checks and all(checks.values()):
            return decision
        if not checks:
            # Если ворота без условий – это финальный fallback.
            return decision
        last_decision = decision
    return last_decision or GateDecision(
        framework_id=framework.id,
        status="unknown",
        checks={},
    )


def _is_better_fact(candidate: Fact, current: Fact) -> bool:
    candidate_conf = candidate.confidence or 0.0
    current_conf = current.confidence or 0.0
    if candidate_conf > current_conf:
        return True
    if candidate_conf < current_conf:
        return False
    return candidate.observed_at >= current.observed_at


def _count_yes(fact: Fact | None, checklist: tuple[str, ...]) -> int:
    payload_checks: Mapping[str, Any]
    if fact is None:
        payload_checks = {}
    else:
        raw_checks = fact.payload.get("checklist", {})
        payload_checks = raw_checks if isinstance(raw_checks, Mapping) else {}
    return sum(1 for key in checklist if bool(payload_checks.get(key)))


def _discretize_yes(count: int) -> float:
    if count >= 4:
        return 1.0
    if count >= 2:
        return 0.5
    return 0.0

