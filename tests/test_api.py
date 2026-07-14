from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient
from api.main import app
from api.routes import denuncias

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
    assert data["scope"] == "COLOMBIA"


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
    assert data["city"] == "COLOMBIA"


def test_stats_endpoint():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert data["city"] == "COLOMBIA"


def test_alerts_endpoint():
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert data["city"] == "COLOMBIA"


def test_global_search_returns_catalog_results():
    response = client.get("/api/v1/buscador/?q=Bucaramanga")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("Bucaramanga" in item["titulo"] for item in data["resultados"])


def test_denuncias_use_persistent_local_storage(monkeypatch, tmp_path):
    database_path = tmp_path / "denuncias.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    denuncias.get_engine.cache_clear()

    payload = {
        "tipo_delito": "Robo / Hurto",
        "descripcion": "Reporte de prueba persistente para validar el servicio.",
        "ciudad": "Bucaramanga",
        "barrio": "Centro",
        "lat": 7.1193,
        "lon": -73.1227,
        "es_anonima": True,
    }
    created = client.post("/api/v1/denuncias/", json=payload)
    assert created.status_code == 200
    assert created.json()["id_denuncia"] == 1

    listed = client.get("/api/v1/denuncias/?ciudad=Bucaramanga")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    nearby = client.get(
        "/api/v1/denuncias/cercanas?lat=7.12&lon=-73.12&radio_km=2"
    )
    assert nearby.status_code == 200
    assert nearby.json()[0]["distancia_km"] < 2

    denuncias.get_engine().dispose()
    denuncias.get_engine.cache_clear()
    with sqlite3.connect(database_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM denuncias_ciudadanas").fetchone()[0] == 1
