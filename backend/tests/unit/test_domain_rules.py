from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.config.frameworks import get_framework
from backend.domain.entities import Fact
from backend.domain.rules import apply_gates, calc_completeness


def _build_fact(letter_cfg, yes_count: int, index: int) -> Fact:
    yes_keys = set(letter_cfg.checklist[:yes_count])
    checklist = {key: key in yes_keys for key in letter_cfg.checklist}
    return Fact(
        deal_id="deal-test",
        kind=letter_cfg.fact_kind,
        payload={"checklist": checklist},
        confidence=0.9,
        observed_at=datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index),
        source="unit-test",
    )


def test_calc_completeness_discretization_bant() -> None:
    framework = get_framework("bant")
    letters = framework.letters_dict()
    facts = [
        _build_fact(letters["B"], 4, 0),
        _build_fact(letters["A"], 2, 1),
        _build_fact(letters["N"], 1, 2),
        _build_fact(letters["T"], 0, 3),
    ]
    completeness = calc_completeness({fact.kind: fact for fact in facts}, framework)

    assert completeness.per_letter["B"] == 1.0
    assert completeness.per_letter["A"] == 0.5
    assert completeness.per_letter["N"] == 0.0
    assert completeness.per_letter["T"] == 0.0
    assert completeness.yes_counts["B"] == 4
    assert completeness.score == pytest.approx(0.375)


def test_apply_gates_bant_go_status() -> None:
    framework = get_framework("bant")
    facts = [
        _build_fact(letter_cfg, 5, index)
        for index, letter_cfg in enumerate(framework.letters)
    ]
    completeness = calc_completeness({fact.kind: fact for fact in facts}, framework)
    decision = apply_gates(completeness, framework)

    assert decision.status == "go"
    assert all(decision.checks.values())


def test_apply_gates_med2ic3_hold_when_go_threshold_not_met() -> None:
    framework = get_framework("med2ic3")
    plan = {
        "M": 5,
        "E": 4,
        "D1": 4,
        "D2": 2,
        "I": 3,
        "C1": 5,
        "C2": 2,
        "C3": 3,
    }
    facts = [
        _build_fact(letter_cfg, plan[letter_cfg.key], index)
        for index, letter_cfg in enumerate(framework.letters)
    ]
    completeness = calc_completeness({fact.kind: fact for fact in facts}, framework)
    decision = apply_gates(completeness, framework)

    assert completeness.score == pytest.approx(0.75)
    assert decision.status == "hold"
    assert decision.checks["score"]
    assert "D2" not in decision.checks



