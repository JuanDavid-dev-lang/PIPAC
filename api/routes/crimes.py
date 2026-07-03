from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import pandas as pd
from pathlib import Path

router = APIRouter(prefix="/api/v1/crimes", tags=["crimes"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@router.get("")
def get_crimes(
    city: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    municipio: Optional[str] = Query(default=None),
    limit: int = 100,
):
    """
    Devuelve delitos. Si existe un parquet específico para una ciudad se usa, sino se usa
    el dataset nacional `crime_hurtos_nacional.parquet` y se aplican filtros por
    departamento/municipio cuando se proporcionen.
    """
    processed_national = PROJECT_ROOT / "datasets" / "processed" / "crime_hurtos_nacional.parquet"
    processed_city = None
    if city:
        processed_city = PROJECT_ROOT / "datasets" / "processed" / f"crime_{city.lower()}.parquet"

    # Elegir archivo de origen
    if processed_city and processed_city.exists():
        path = processed_city
    elif processed_national.exists():
        path = processed_national
    else:
        return {"items": [], "warning": "Datasets no cargados. Correr refresh."}

    try:
        df = pd.read_parquet(path)

        # Normalizar mayúsculas en columnas de texto si existen
        for col in ["municipio", "barrio", "departamento", "comuna"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # Aplicar filtros opcionales
        if department:
            if "departamento" in df.columns:
                df = df[df["departamento"].str.upper() == department.upper()]
            elif "comuna" in df.columns:
                df = df[df["comuna"].str.upper() == department.upper()]

        if municipio:
            if "municipio" in df.columns:
                df = df[df["municipio"].str.upper() == municipio.upper()]
            elif "barrio" in df.columns:
                df = df[df["barrio"].str.upper() == municipio.upper()]

        # Si se pasa `city` y estamos usando el dataset nacional, intentamos filtrar
        if city and path.name == "crime_hurtos_nacional.parquet":
            if "municipio" in df.columns:
                df = df[df["municipio"].str.upper() == city.upper()]
            elif "barrio" in df.columns:
                df = df[df["barrio"].str.upper() == city.upper()]

        subset = df.head(limit).to_dict(orient="records")
        return {"source_file": path.name, "total_records": len(df), "limit": limit, "items": subset}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


