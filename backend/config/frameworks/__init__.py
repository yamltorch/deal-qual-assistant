"""Загрузка конфигураций фреймворков BANT и MED2IC3."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import yaml

_BASE_DIR = Path(__file__).resolve().parent
_FRAMEWORK_FILES: dict[str, str] = {
    "bant": "bant.yaml",
    "med2ic3": "med2ic3.yaml",
}


@dataclass(frozen=True, slots=True)
class LetterConfig:
    key: str
    title: str
    fact_kind: str
    weight: float
    checklist: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GateConfig:
    status: str
    min_score: float | None
    required_letters: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class FrameworkConfig:
    id: str
    name: str
    priority: int
    letters: tuple[LetterConfig, ...]
    gates: tuple[GateConfig, ...]

    def letters_dict(self) -> dict[str, LetterConfig]:
        return {letter.key: letter for letter in self.letters}


def available_frameworks() -> tuple[str, ...]:
    return tuple(_FRAMEWORK_FILES.keys())


@lru_cache(maxsize=len(_FRAMEWORK_FILES))
def get_framework(framework_id: str) -> FrameworkConfig:
    try:
        file_name = _FRAMEWORK_FILES[framework_id]
    except KeyError as exc:  # pragma: no cover - защита от опечаток
        raise KeyError(f"Неизвестный фреймворк: {framework_id}") from exc
    data = _load_yaml(_BASE_DIR / file_name)
    return _build_framework(framework_id, data)


def get_frameworks(framework_ids: Iterable[str]) -> tuple[FrameworkConfig, ...]:
    return tuple(get_framework(framework_id) for framework_id in framework_ids)


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _build_framework(framework_id: str, raw: Any) -> FrameworkConfig:
    if not isinstance(raw, dict):
        raise ValueError(f"Некорректный YAML для {framework_id}: ожидался mapping")
    letters_raw = raw.get("letters", [])
    gates_raw = raw.get("gates", [])
    letters = tuple(_build_letter(item) for item in letters_raw)
    gates = tuple(_build_gate(item) for item in gates_raw)
    if not letters:
        raise ValueError(f"В конфигурации {framework_id} нет букв")
    if not gates:
        raise ValueError(f"В конфигурации {framework_id} нет ворот")
    name = str(raw.get("name", framework_id.upper()))
    priority = int(raw.get("priority", 100))
    total_weight = sum(letter.weight for letter in letters)
    if not 0.99 <= total_weight <= 1.01:
        raise ValueError(f"Сумма весов букв для {framework_id} должна быть около 1.0, сейчас: {total_weight}")
    return FrameworkConfig(
        id=framework_id,
        name=name,
        priority=priority,
        letters=letters,
        gates=gates,
    )


def _build_letter(item: Any) -> LetterConfig:
    if not isinstance(item, dict):
        raise ValueError("Ожидался словарь с настройками буквы")
    try:
        key = str(item["key"])
        title = str(item["title"])
        fact_kind = str(item.get("fact_kind", key))
        weight = float(item["weight"])
    except KeyError as exc:
        raise ValueError("В букве пропущено обязательное поле") from exc
    checklist_raw = item.get("checklist", [])
    checklist: tuple[str, ...] = tuple(str(check) for check in checklist_raw)
    if not checklist:
        raise ValueError(f"У буквы {key} отсутствует чек-лист")
    return LetterConfig(
        key=key,
        title=title,
        fact_kind=fact_kind,
        weight=weight,
        checklist=checklist,
    )


def _build_gate(item: Any) -> GateConfig:
    if not isinstance(item, dict):
        raise ValueError("Ожидался словарь с настройками ворот")
    try:
        status = str(item["status"])
    except KeyError as exc:
        raise ValueError("Для ворот необходимо поле status") from exc
    min_score = item.get("min_score")
    min_score_value = float(min_score) if min_score is not None else None
    required = item.get("required_letters", {})
    if isinstance(required, dict):
        required_items = tuple(
            (str(letter), float(value)) for letter, value in required.items()
        )
    elif isinstance(required, list):
        required_items = tuple(
            (str(pair["letter"]), float(pair["min"]))
            for pair in required
            if isinstance(pair, dict)
        )
    else:
        required_items = tuple()
    return GateConfig(status=status, min_score=min_score_value, required_letters=required_items)


__all__ = (
    "FrameworkConfig",
    "GateConfig",
    "LetterConfig",
    "available_frameworks",
    "get_framework",
    "get_frameworks",
)
