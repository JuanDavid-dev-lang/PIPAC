from fastapi import APIRouter, Query
from typing import List, Dict, Any
from datetime import date

router = APIRouter(prefix="/api/v1/predictions", tags=["Inteligencia Artificial - Riesgo"])

@router.get("/risk-map", summary="Mapa de Riesgo (Heatmap GeoJSON)")
def get_risk_map(target_date: date = None, region_id: str = None):
    # TODO: Inferencia del modelo XGBoost espacial
    # Retornamos el formato que usará leaflet.heat: [lat, lng, intensidad]
    return {
        "heatmap_data": [
            [4.6097, -74.0817, 1.0], [4.6200, -74.0900, 0.8], [4.5900, -74.0800, 0.9],
            [6.2442, -75.5812, 0.9], [6.2500, -75.5700, 0.7], [6.2600, -75.5600, 0.6],
            [3.4516, -76.5320, 0.95], [3.4400, -76.5400, 0.85],
            [10.9639, -74.7964, 0.8], [10.9700, -74.8000, 0.7],
            [7.1193, -73.1227, 0.6]
        ],
        "model_version": "v2.0-XGB-National"
    }

@router.get("/alerts", summary="Alertas Predictivas Generadas por IA")
def get_ai_alerts(region_id: str = None):
    return {
        "alerts": [
            {
                "level": "HIGH",
                "message": "El modelo XGBoost proyecta un incremento del 15% en hurto a personas en la localidad de Chapinero (Bogotá) entre las 18:00 y 21:00 horas.",
                "recommendation": "Priorizar patrullaje y activar cuadrantes 4 y 5."
            }
        ]
    }

@router.get("/trend", summary="Proyección de Tendencias por ML")
def get_ml_trends(city: str = Query(..., description="Nombre de la ciudad")):
    return {
        "city": city,
        "trend_data": [
            {"time": "00:00", "predicted_crimes": 12}, 
            {"time": "04:00", "predicted_crimes": 5}, 
            {"time": "08:00", "predicted_crimes": 15}, 
            {"time": "12:00", "predicted_crimes": 25},
            {"time": "16:00", "predicted_crimes": 30}, 
            {"time": "20:00", "predicted_crimes": 45}
        ]
    }
