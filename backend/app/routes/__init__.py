"""Регистрация маршрутов FastAPI приложения."""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.routes import events, health, state


def setup_routes(app: FastAPI) -> None:
    """Подключить все маршруты приложения."""

    app.include_router(health.router)
    app.include_router(state.router)
    app.include_router(events.router)


