"""Чистые шаги пересчёта read-model сделки."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from pydantic import BaseModel, ConfigDict

from backend.config.frameworks import FrameworkConfig
from backend.domain.entities import DealReadModel, Fact
from backend.domain.rules import apply_gates, calc_completeness, resolve_conflicts
from backend.domain.value_objects import FrameworkCompleteness, GateDecision


class RecomputeInput(BaseModel):
    """Входные данные пайплайна пересчёта."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    deal_id: str
    facts: list[Fact]
    frameworks: list[FrameworkConfig]


class ResolveContext(RecomputeInput):
    """Контекст после шага resolve."""

    resolved: dict[str, Fact]


class CompletenessContext(ResolveContext):
    """Контекст после вычисления completeness."""

    completeness: dict[str, FrameworkCompleteness]


class GatesContext(CompletenessContext):
    """Контекст после применения ворот."""

    gates: dict[str, GateDecision]


def resolve_step(ctx: RecomputeInput) -> ResolveContext:
    """Выбрать лучшие факты по видам."""

    resolved = resolve_conflicts(ctx.facts)
    return ResolveContext(
        deal_id=ctx.deal_id,
        facts=ctx.facts,
        frameworks=ctx.frameworks,
        resolved=resolved,
    )


def completeness_step(ctx: ResolveContext) -> CompletenessContext:
    """Рассчитать completeness и score по каждому фреймворку."""

    completeness = {
        framework.id: calc_completeness(ctx.resolved, framework)
        for framework in ctx.frameworks
    }
    return CompletenessContext(
        deal_id=ctx.deal_id,
        facts=ctx.facts,
        frameworks=ctx.frameworks,
        resolved=ctx.resolved,
        completeness=completeness,
    )


def gates_step(ctx: CompletenessContext) -> GatesContext:
    """Определить статусы по воротам для всех фреймворков."""

    gates = {
        framework.id: apply_gates(ctx.completeness[framework.id], framework)
        for framework in ctx.frameworks
    }
    return GatesContext(
        deal_id=ctx.deal_id,
        facts=ctx.facts,
        frameworks=ctx.frameworks,
        resolved=ctx.resolved,
        completeness=ctx.completeness,
        gates=gates,
    )


def assemble_read_model_step(ctx: GatesContext) -> DealReadModel:
    """Собрать финальную read-model из результатов шагов."""

    letters_payload: dict[str, dict[str, object]] = {}
    selected_status = "unknown"
    selected_score: float | None = None
    for framework in sorted(ctx.frameworks, key=lambda item: item.priority):
        completeness = ctx.completeness[framework.id]
        decision = ctx.gates[framework.id]
        letters_payload[framework.id] = {
            "framework": framework.name,
            "status": decision.status,
            "score": completeness.score,
            "per_letter": dict(completeness.per_letter),
            "yes_counts": dict(completeness.yes_counts),
            "gate_checks": dict(decision.checks),
        }
        if selected_score is None:
            selected_status = decision.status
            selected_score = completeness.score
    return DealReadModel(
        deal_id=ctx.deal_id,
        status=selected_status,
        score=selected_score,
        last_event=None,
        updated_at=_max_observed(ctx.resolved.values()),
        letters=letters_payload,
    )


def recompute_read_model(ctx: RecomputeInput) -> DealReadModel:
    """Полностью выполнить пайплайн пересчёта."""

    resolved_ctx = resolve_step(ctx)
    completeness_ctx = completeness_step(resolved_ctx)
    gates_ctx = gates_step(completeness_ctx)
    return assemble_read_model_step(gates_ctx)


def _max_observed(facts: Iterable[Fact]) -> datetime | None:
    timestamps = [fact.observed_at for fact in facts]
    return max(timestamps) if timestamps else None


__all__ = [
    "RecomputeInput",
    "resolve_step",
    "completeness_step",
    "gates_step",
    "assemble_read_model_step",
    "recompute_read_model",
]
