from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config.settings import settings
from api.routes.health import router as health_router
from api.routes.crimes import router as crimes_router
from api.routes.predictions import router as predictions_router
from api.routes.stats import router as stats_router
from api.routes.alerts import router as alerts_router
from api.routes.admin import router as admin_router
from api.routes.territorios import router as territorios_router
from api.routes.entidades import router as entidades_router
from api.routes.buscador import router as buscador_router
from api.routes.denuncias import router as denuncias_router
from preprocessing.etl import run_default_etl

# Módulo Últimas Denuncias Nacionales
from modules.latest_reports.api.router import router as latest_reports_router


app = FastAPI(
    title="Plataforma Inteligente para la Prediccion y Analisis de Criminalidad",
    version="0.1.0",
    description="API REST para delitos, predicciones, mapas, estadisticas y alertas.",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

app.include_router(health_router)
app.include_router(crimes_router)
app.include_router(predictions_router)
app.include_router(stats_router)
app.include_router(alerts_router)
app.include_router(admin_router)
app.include_router(territorios_router)
app.include_router(entidades_router)
app.include_router(buscador_router)
app.include_router(denuncias_router)
app.include_router(latest_reports_router)



@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/meta")
def meta():
    return {
        "project_root": str(PROJECT_ROOT),
        "scope": settings.default_city,
        "note": "Conecta datos.gov.co, ETL nacional, PostGIS, FastAPI y Dash.",
    }


@app.post("/api/v1/datasets/refresh/local")
def refresh_datasets_local(split: bool = False):
    """Refresca los datasets localmente. Si `split=true`, divide el dataset nacional por municipio.
    Usar: `curl -X POST 'http://.../api/v1/datasets/refresh/local?split=true'`
    """
    results = run_default_etl(PROJECT_ROOT, split_national=split)
    return {"results": [r.__dict__ for r in results]}
