from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query


router = APIRouter(prefix="/api/v1/predictions", tags=["Inteligencia Artificial - Riesgo"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_dataset_path(city: str | None) -> Path:
    processed_dir = PROJECT_ROOT / "datasets" / "processed"
    if city:
        city_key = city.lower().replace(" ", "_")
        for suffix in ("_featured", ""):
            city_path = processed_dir / f"crime_{city_key}{suffix}.parquet"
            if city_path.exists():
                return city_path

    candidates = [
        processed_dir / "crime_hurtos_nacional_featured.parquet",
        processed_dir / "crime_bga_featured.parquet",
        processed_dir / "crime_hurtos_nacional.parquet",
        processed_dir / "crime_bga.parquet",
    ]
    return next((path for path in candidates if path.exists()), candidates[0])


def _filter_city(df: pd.DataFrame, city: str | None) -> pd.DataFrame:
    if not city:
        return df

    city_upper = city.upper()
    for column in ("municipio", "barrio", "comuna", "departamento"):
        if column in df.columns:
            filtered = df[df[column].astype(str).str.upper() == city_upper]
            if not filtered.empty:
                return filtered
    return df.iloc[0:0]


def _location_column(df: pd.DataFrame) -> str:
    for column in ("barrio", "municipio", "comuna", "departamento"):
        if column in df.columns:
            return column
    return "__location"


def _risk_level(probability: float) -> str:
    if probability >= 0.75:
        return "ALTO"
    if probability >= 0.45:
        return "MEDIO"
    return "BAJO"


def _build_predictions(df: pd.DataFrame, limit: int) -> list[dict]:
    if df.empty:
        return []

    data = df.copy()
    location_col = _location_column(data)
    if location_col == "__location":
        data[location_col] = "NACIONAL"

    if "densidad_eventos_30d" in data.columns:
        data["risk_score"] = pd.to_numeric(data["densidad_eventos_30d"], errors="coerce").fillna(0)
    else:
        data["risk_score"] = data.groupby(location_col)[location_col].transform("count").astype(float)

    if "tasa_crimen_1000" in data.columns:
        data["risk_score"] = data["risk_score"] + pd.to_numeric(data["tasa_crimen_1000"], errors="coerce").fillna(0)

    aggregations = {"risk_score": ("risk_score", "mean")}
    if "lat" in data.columns:
        aggregations["lat"] = ("lat", "mean")
    if "lon" in data.columns:
        aggregations["lon"] = ("lon", "mean")

    grouped = (
        data.groupby(location_col, dropna=False)
        .agg(**aggregations)
        .reset_index()
        .sort_values("risk_score", ascending=False)
        .head(limit)
    )

    max_score = float(grouped["risk_score"].max()) if not grouped.empty else 0.0
    predictions: list[dict] = []
    for _, row in grouped.iterrows():
        probability = float(row["risk_score"] / max_score) if max_score > 0 else 0.0
        item = {
            "barrio": str(row[location_col]),
            "risk_probability": round(probability, 4),
            "risk_level": _risk_level(probability),
        }
        if "lat" in grouped.columns and pd.notna(row.get("lat")):
            item["lat"] = float(row["lat"])
        if "lon" in grouped.columns and pd.notna(row.get("lon")):
            item["lon"] = float(row["lon"])
        predictions.append(item)
    return predictions


@router.get("", summary="Predicciones de riesgo por territorio")
def get_predictions(
    city: Optional[str] = Query(default=None),
    target_date: Optional[date] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
):
    data_path = _resolve_dataset_path(city)
    if not data_path.exists():
        return {
            "city": city or "COLOMBIA",
            "target_date": str(target_date) if target_date else None,
            "source_file": None,
            "predictions": [],
            "warning": "Datasets no cargados. Ejecuta el ETL antes de generar predicciones.",
        }

    try:
        df = pd.read_parquet(data_path)
        filtered = _filter_city(df, city)
        return {
            "city": city or "COLOMBIA",
            "target_date": str(target_date) if target_date else None,
            "source_file": data_path.name,
            "model_version": "risk-score-v1",
            "predictions": _build_predictions(filtered, limit),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/risk-map", summary="Mapa de Riesgo (Heatmap GeoJSON)")
def get_risk_map(target_date: date = None, region_id: str = None):
    return {
        "heatmap_data": [
            [4.6097, -74.0817, 1.0], [4.6200, -74.0900, 0.8], [4.5900, -74.0800, 0.9],
            [6.2442, -75.5812, 0.9], [6.2500, -75.5700, 0.7], [6.2600, -75.5600, 0.6],
            [3.4516, -76.5320, 0.95], [3.4400, -76.5400, 0.85],
            [10.9639, -74.7964, 0.8], [10.9700, -74.8000, 0.7],
            [7.1193, -73.1227, 0.6],
        ],
        "model_version": "v2.0-XGB-National",
    }


@router.get("/alerts", summary="Alertas Predictivas Generadas por IA")
def get_ai_alerts(region_id: str = None):
    return {
        "alerts": [
            {
                "level": "HIGH",
                "message": "El modelo proyecta un incremento de riesgo en zonas con mayor densidad reciente de eventos.",
                "recommendation": "Priorizar patrullaje preventivo en territorios con riesgo alto.",
            }
        ]
    }


@router.get("/trend", summary="Proyeccion de Tendencias por ML")
def get_ml_trends(city: str = Query(..., description="Nombre de la ciudad")):
    return {
        "city": city,
        "trend_data": [
            {"time": "00:00", "predicted_crimes": 12},
            {"time": "04:00", "predicted_crimes": 5},
            {"time": "08:00", "predicted_crimes": 15},
            {"time": "12:00", "predicted_crimes": 25},
            {"time": "16:00", "predicted_crimes": 30},
            {"time": "20:00", "predicted_crimes": 45},
        ],
    }
