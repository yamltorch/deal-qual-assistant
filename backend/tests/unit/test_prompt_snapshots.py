from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jinja2 import Environment, FileSystemLoader
from jsonschema import Draft202012Validator

from backend.config.frameworks import get_framework

_ROOT = Path(__file__).resolve().parents[3]
_PROMPTS_DIR = _ROOT / "backend" / "prompts"
_PREPROMPT = (_ROOT / "preprompt.txt").read_text(encoding="utf-8").rstrip()
_SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "snapshots"
_ENV = Environment(
    loader=FileSystemLoader(str(_PROMPTS_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def _render(group: str, template: str, ctx: dict[str, Any]) -> str:
    data = dict(ctx)
    if template == "system.jinja":
        data["preprompt"] = _PREPROMPT
    return _ENV.get_template(f"{group}/{template}").render(**data)


def _combine_prompt(group: str, ctx: dict[str, Any]) -> str:
    system = _render(group, "system.jinja", ctx)
    user = _render(group, "user.jinja", ctx)
    return "\n".join(
        [
            f"=== {group.upper()} :: SYSTEM ===",
            system,
            f"=== {group.upper()} :: USER ===",
            user,
            "",
        ]
    )


def _assert_snapshot(name: str, content: str) -> None:
    path = _SNAPSHOT_DIR / name
    if not path.exists():
        raise AssertionError(f"Snapshot {name} is missing at {path}")
    expected = path.read_text(encoding="utf-8")
    assert content == expected


def _base_crm() -> dict[str, Any]:
    return {
        "ID сделки": 501,
        "Название сделки": "Modern Data Platform",
        "Ответственный": "Анна Петрова",
        "Этап": "Подготовка закупки",
        "Дата перехода на этап": "2025-01-12",
        "Статус сделки": "Открыта",
        "Ожидаемая выручка с НДС": 12500000,
        "Ожидаемая выручка без НДС": 10416667,
        "НДС": "20%",
    }


def _extract_ctx(framework_id: str) -> dict[str, Any]:
    crm = _base_crm()
    free_text = "Менеджер обновил данные: бюджет подтверждён, ждём тендер."
    chat_list = [
        {"role": "manager", "text": "Клиент подтвердил бюджет 12.5 млн ₽."},
        {"role": "client", "text": "Финансовый директор вернётся с тендера 5 февраля."},
    ]
    if framework_id == "med2ic3":
        crm.update(
            {
                "Плановая дата запуска": "2025-04-01",
                "Дата финального согласования": "2025-03-10",
                "Текущая конкуренция": "Вендор X",
            }
        )
        free_text = "Обнаружен рисковый дедлайн: аудит до 2025-03-05."
        chat_list.append({"role": "manager", "text": "Нужно успеть к аудиту 5 марта."})
    return {
        "framework": framework_id.upper(),
        "crm": crm,
        "chat_list": chat_list,
        "chat_map": {},
        "free_text": free_text,
    }


def _reasoner_ctx(framework_id: str) -> dict[str, Any]:
    framework = get_framework(framework_id)
    letters = [{"key": letter.key, "title": letter.title} for letter in framework.letters]
    per_letter = {letter["key"]: 0.5 for letter in letters}
    yes_counts = {letter["key"]: 3 for letter in letters}
    deal = {
        "id": "DEAL-501",
        "name": "Modern Data Platform",
        "stage": "Подготовка закупки" if framework_id == "bant" else "Решение",
        "updated_at": "2025-01-18T10:00:00Z",
    }
    facts_by_letter: dict[str, list[dict[str, Any]]] = {}
    facts_by_letter["B" if framework_id == "bant" else "M"] = [
        {
            "facet": "budget.amount" if framework_id == "bant" else "metrics.expected_lift",
            "value": {"amount": 12500000, "currency": "RUB"} if framework_id == "bant" else {"metric": "GM", "delta": 0.12},
            "source": "crm",
            "evidence": "Ожидаемая выручка с НДС: 12500000",
            "confidence": 0.9,
            "ts": "2025-01-12",
        }
    ]
    if framework_id == "med2ic3":
        facts_by_letter["C3"] = [
            {
                "facet": "timeline.compelling_event",
                "value": {"date": "2025-03-05", "description": "Финансовый аудит"},
                "source": "chat",
                "evidence": "Нужно успеть к аудиту 5 марта.",
                "confidence": 0.8,
                "ts": "2025-01-16",
            }
        ]
    else:
        facts_by_letter["T"] = [
            {
                "facet": "timeline.target_date",
                "value": "2025-02-15",
                "source": "crm",
                "evidence": "Ожидаемая дата подписания: 2025-02-15",
                "confidence": 0.7,
                "ts": "2025-01-12",
            }
        ]
    decision = {
        "status": "hold",
        "score": 0.65 if framework_id == "bant" else 0.7,
        "reason": "Не все буквы закрыты",
        "confidence": 0.6,
    }
    ctx = _extract_ctx(framework_id)
    ctx.update(
        {
            "deal": deal,
            "decision": decision,
            "completeness": {"per_letter": per_letter, "yes_counts": yes_counts},
            "letters": letters,
            "facts_by_letter": facts_by_letter,
            "allow_manager_question": framework_id == "bant",
        }
    )
    return ctx


def _arbiter_ctx(framework_id: str) -> dict[str, Any]:
    ctx = _extract_ctx(framework_id)
    letter = "B" if framework_id == "bant" else "C3"
    ctx.update(
        {
            "facet": {"name": "budget.amount" if framework_id == "bant" else "timeline.compelling_event", "letter": letter},
            "conflict_reason": "Конфликт данных между CRM и перепиской",
            "current_fact": None,
            "candidates": [
                {
                    "id": "crm-1",
                    "value": {"amount": 12500000, "currency": "RUB"} if framework_id == "bant" else {"date": "2025-03-10", "description": "Финал согласования"},
                    "source": "crm",
                    "confidence": 0.85,
                    "evidence": "CRM зафиксировала значение.",
                    "ts": "2025-01-12T09:00:00Z",
                },
                {
                    "id": "chat-1",
                    "value": {"amount": 11800000, "currency": "RUB"} if framework_id == "bant" else {"date": "2025-03-05", "description": "Финансовый аудит"},
                    "source": "chat",
                    "confidence": 0.75,
                    "evidence": "Из переписки: нужно успеть к аудиту 5 марта.",
                    "ts": "2025-01-16T14:00:00Z",
                },
            ],
        }
    )
    return ctx


@pytest.mark.parametrize("framework_id", ["bant", "med2ic3"])
def test_extract_prompts_snapshot(framework_id: str) -> None:
    rendered = _combine_prompt("extract", _extract_ctx(framework_id))
    _assert_snapshot(f"extract_{framework_id}.txt", rendered)


@pytest.mark.parametrize("framework_id", ["bant", "med2ic3"])
def test_reasoner_prompts_snapshot(framework_id: str) -> None:
    rendered = _combine_prompt("reasoner", _reasoner_ctx(framework_id))
    _assert_snapshot(f"reasoner_{framework_id}.txt", rendered)


@pytest.mark.parametrize("framework_id", ["bant", "med2ic3"])
def test_arbiter_prompts_snapshot(framework_id: str) -> None:
    rendered = _combine_prompt("arbiter", _arbiter_ctx(framework_id))
    _assert_snapshot(f"arbiter_{framework_id}.txt", rendered)


@pytest.mark.parametrize(
    "schema_name",
    [
        "extract/schema.extract.json",
        "reasoner/schema.reasoner.json",
        "arbiter/schema.arbiter.json",
    ],
)
def test_json_schemas_are_valid(schema_name: str) -> None:
    schema_path = _PROMPTS_DIR / schema_name
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(data)

