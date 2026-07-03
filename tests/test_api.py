from __future__ import annotations

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_meta():
    response = client.get("/meta")
    assert response.status_code == 200
    data = response.json()
    assert "project_root" in data
    assert data["city"] == "BUCARAMANGA"


def test_crimes_endpoint():
    response = client.get("/api/v1/crimes?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "city" in data


def test_crimes_filter_municipio():
    # Probar que el endpoint acepta filtro por municipio/ciudad
    response = client.get("/api/v1/crimes?municipio=BOGOT\u00c1&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_records" in data or "warning" in data


def test_predictions_endpoint():
    response = client.get("/api/v1/predictions")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data


def test_stats_endpoint():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data


def test_alerts_endpoint():
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
