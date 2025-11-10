"""Проверка ограничений читаемости кода."""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterable

MAX_FILE_LINES = 150
MAX_FUNCTION_LINES = 50
MAX_LINE_LENGTH = 100
IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}


def iter_python_files(root: Path) -> Iterable[Path]:
    """Итерироваться по python-файлам проекта, исключая служебные папки."""

    for path in root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def check_file(path: Path) -> list[str]:
    """Вернуть список нарушений ограничений для файла."""

    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > MAX_FILE_LINES:
        errors.append(
            f"{path}: превышен лимит строк {len(lines)}>{MAX_FILE_LINES}",
        )
    for idx, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            errors.append(
                f"{path}:{idx}: строка длиной {len(line)}>{MAX_LINE_LENGTH}",
            )
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:  # pragma: no cover - синтаксис проверяет сам интерпретатор
        errors.append(f"{path}: синтаксическая ошибка: {exc}")
        return errors
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.end_lineno is None or node.lineno is None:
                continue
            length = node.end_lineno - node.lineno + 1
            if length > MAX_FUNCTION_LINES:
                errors.append(
                    f"{path}:{node.lineno}: функция {node.name!r} длиннее лимита "
                    f"{length}>{MAX_FUNCTION_LINES}",
                )
    return errors


def main() -> int:
    """Точка входа скрипта."""

    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    for path in iter_python_files(root):
        errors.extend(check_file(path))
    if errors:
        for message in errors:
            print(message)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


