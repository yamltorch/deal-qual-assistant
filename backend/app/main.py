"""Точка входа FastAPI приложения."""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.routes import setup_routes

app = FastAPI(
    title="Deal Qual Assistant",
    version="0.1.0",
)
setup_routes(app)


@app.get("/")
def read_root() -> dict[str, str]:
    """Простая заглушка корневого маршрута."""

    return {"message": "Deal Qual Assistant backend"}


