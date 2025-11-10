"""Тесты здоровья API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_returns_ok() -> None:
    """GET /health отдаёт статус 200 и ok=true."""

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


