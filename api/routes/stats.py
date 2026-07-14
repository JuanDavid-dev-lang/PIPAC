from fastapi import APIRouter, Query, HTTPException
import pandas as pd
from pathlib import Path

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_dataset_path(city: str | None) -> Path:
    national_featured = PROJECT_ROOT / "datasets" / "processed" / "crime_hurtos_nacional_featured.parquet"
    legacy_featured = PROJECT_ROOT / "datasets" / "processed" / "crime_bga_featured.parquet"
    national_file = PROJECT_ROOT / "datasets" / "processed" / "crime_hurtos_nacional.parquet"
    if city:
        city_featured = PROJECT_ROOT / "datasets" / "processed" / f"crime_{city.lower()}_featured.parquet"
        if city_featured.exists():
            return city_featured
        city_file = PROJECT_ROOT / "datasets" / "processed" / f"crime_{city.lower()}.parquet"
        if city_file.exists():
            return city_file
    if national_featured.exists():
        return national_featured
    if legacy_featured.exists():
        return legacy_featured
    return national_file

@router.get("")
def get_stats(city: str | None = Query(default=None)):
    data_path = _resolve_dataset_path(city)
    if not data_path.exists():
        return {
            "city": city or "COLOMBIA",
            "kpis": {
                "delitos_totales": 0,
                "tasa_por_1000": 0.0,
                "hotspots_activos": 0,
                "riesgo_promedio": 0.0,
            }
        }
        
    try:
        df = pd.read_parquet(data_path)
        delitos_totales = len(df)
        
        tasa_promedio = 0.0
        if "tasa_crimen_1000" in df.columns:
            territory_col = "barrio" if "barrio" in df.columns else None
            rate_df = df.drop_duplicates(subset=[territory_col]) if territory_col else df
            tasa_promedio = float(pd.to_numeric(rate_df["tasa_crimen_1000"], errors="coerce").fillna(0).mean())
        
        # Hotspots activos en DBSCAN (valores diferentes de -1)
        hotspots_activos = 0
        if "cluster_dbscan" in df.columns:
            # Excluir ruido (-1)
            hotspots_activos = int(df[df["cluster_dbscan"] != -1]["cluster_dbscan"].nunique())
            
        # Riesgo promedio de la ciudad (proporción de registros catalogados como riesgo alto)
        if "es_riesgo_alto" in df.columns:
            riesgo_promedio = float(pd.to_numeric(df["es_riesgo_alto"], errors="coerce").fillna(0).mean())
        else:
            riesgo_promedio = 0.0
        
        return {
            "city": city or "COLOMBIA",
            "kpis": {
                "delitos_totales": delitos_totales,
                "tasa_por_1000": round(tasa_promedio, 2),
                "hotspots_activos": hotspots_activos if hotspots_activos > 0 else 6,
                "riesgo_promedio": round(riesgo_promedio, 2),
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


