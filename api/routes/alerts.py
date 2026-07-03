from fastapi import APIRouter, Query, HTTPException
import pandas as pd
from pathlib import Path
from utils.ai_advisor import AIAdvisor

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]

@router.get("")
def get_alerts(city: str = Query(default="BUCARAMANGA")):
    data_path = PROJECT_ROOT / "datasets" / "processed" / "crime_bga_featured.parquet"
    if not data_path.exists():
        return {
            "city": city,
            "alerts": [
                "Alerta inicial: El sistema requiere entrenamiento o carga de datos para generar alertas por IA."
            ]
        }
        
    try:
        df = pd.read_parquet(data_path)
        advisor = AIAdvisor(df)
        recs = advisor.get_police_presence_recommendations()
        return {"city": city, "alerts": recs}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


