from datetime import date
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
import pandas as pd
import joblib

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]

@router.get("")
def get_predictions(target_date: date | None = None, city: str = Query(default="BUCARAMANGA")):
    model_path = PROJECT_ROOT / "models" / "xgb.joblib"
    crime_path = PROJECT_ROOT / "models" / "dbscan_hotspots.joblib"
    city_file = PROJECT_ROOT / "datasets" / "processed" / f"crime_{city.lower()}.parquet"
    national_file = PROJECT_ROOT / "datasets" / "processed" / "crime_hurtos_nacional.parquet"
    data_path = city_file if city_file.exists() else national_file

    if not (model_path.exists() and data_path.exists()):
        return {
            "city": city,
            "target_date": str(target_date or date.today()),
            "predictions": [],
            "warning": "Modelos o datasets procesados no encontrados. Ejecutar entrenamiento."
        }
        
    try:
        # Cargar modelo y datos
        model = joblib.load(model_path)
        df = pd.read_parquet(data_path)
        
        # Tomar una muestra representativa por barrio para mañana
        barrio_df = df.drop_duplicates(subset=["barrio"]).copy()
        
        # Simular fecha objetivo
        target = target_date or date.today()
        barrio_df["fecha_hora"] = pd.to_datetime(str(target))
        barrio_df["anio"] = target.year
        barrio_df["mes"] = target.month
        barrio_df["dia"] = target.day
        barrio_df["dia_semana"] = barrio_df["fecha_hora"].dt.dayofweek
        barrio_df["hora"] = 20  # Inferencia para horario nocturno pico
        barrio_df["semana_anio"] = barrio_df["fecha_hora"].dt.isocalendar().week.astype("Int64")
        barrio_df["es_fin_de_semana"] = barrio_df["dia_semana"].isin([5, 6]).astype(int)
        
        # Realizar predicciones
        preds = model.predict(barrio_df)
        probs = model.predict_proba(barrio_df)[:, 1]
        
        barrio_df["pred_riesgo"] = preds
        barrio_df["prob_riesgo"] = probs
        
        result_list = []
        for _, row in barrio_df.iterrows():
            result_list.append({
                "barrio": str(row["barrio"]),
                "comuna": str(row["comuna"]) if "comuna" in row else "N/A",
                "lat": float(row["lat"]) if "lat" in row else 7.119,
                "lon": float(row["lon"]) if "lon" in row else -73.116,
                "risk_probability": round(float(row["prob_riesgo"]), 3),
                "risk_level": "ALTO" if row["pred_riesgo"] == 1 else "BAJO",
                "hotspot_cluster": int(row["cluster_dbscan"]) if "cluster_dbscan" in row else -1
            })
            
        # Ordenar por probabilidad de riesgo decreciente
        result_list = sorted(result_list, key=lambda x: x["risk_probability"], reverse=True)
        
        return {
            "city": city,
            "target_date": str(target),
            "total_barrios_evaluados": len(result_list),
            "predictions": result_list
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


