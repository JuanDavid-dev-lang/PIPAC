from fastapi import APIRouter, Query, HTTPException
import pandas as pd
from pathlib import Path
from utils.ai_advisor import AIAdvisor

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

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
def get_alerts(city: str | None = Query(default=None)):
    data_path = _resolve_dataset_path(city)
    if not data_path.exists():
        return {
            "city": city or "COLOMBIA",
            "alerts": [
                "Alerta inicial: El sistema requiere entrenamiento o carga de datos para generar alertas por IA."
            ]
        }
        
    try:
        df = pd.read_parquet(data_path)
        advisor = AIAdvisor(df)
        recs = advisor.get_police_presence_recommendations()
        return {"city": city or "COLOMBIA", "alerts": recs}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


