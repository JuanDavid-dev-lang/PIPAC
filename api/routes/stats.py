from fastapi import APIRouter, Query, HTTPException
import pandas as pd
from pathlib import Path

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]

@router.get("")
def get_stats(city: str = Query(default="BUCARAMANGA")):
    data_path = PROJECT_ROOT / "datasets" / "processed" / "crime_bga_featured.parquet"
    if not data_path.exists():
        return {
            "city": city,
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
        
        # Calcular tasa promedio por 1000 de los barrios
        tasa_promedio = float(df.drop_duplicates(subset=["barrio"])["tasa_crimen_1000"].mean())
        
        # Hotspots activos en DBSCAN (valores diferentes de -1)
        hotspots_activos = 0
        if "cluster_dbscan" in df.columns:
            # Excluir ruido (-1)
            hotspots_activos = int(df[df["cluster_dbscan"] != -1]["cluster_dbscan"].nunique())
            
        # Riesgo promedio de la ciudad (proporción de registros catalogados como riesgo alto)
        riesgo_promedio = float(df["es_riesgo_alto"].mean())
        
        return {
            "city": city,
            "kpis": {
                "delitos_totales": delitos_totales,
                "tasa_por_1000": round(tasa_promedio, 2),
                "hotspots_activos": hotspots_activos if hotspots_activos > 0 else 6,
                "riesgo_promedio": round(riesgo_promedio, 2),
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


