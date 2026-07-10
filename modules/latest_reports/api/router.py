from fastapi import APIRouter, Depends, Query
from typing import Optional
import json

from .schemas import (
    ReportListResponse,
    StatisticsResponse,
    GeoFeatureCollection,
    TimelineResponse,
    FilterParams,
    ChatRequest,
    ChatResponse
)
from .dependencies import get_parquet_store, get_cache_manager
from ..loader.parquet_store import ParquetStore
from ..cache.cache_manager import CacheManager

router = APIRouter(prefix='/api/v1/latest-reports', tags=['Últimas Denuncias Nacionales'])

@router.get("/", response_model=ReportListResponse)
def get_reports(
    filters: FilterParams = Depends(),
    store: ParquetStore = Depends(get_parquet_store),
    cache: CacheManager = Depends(get_cache_manager)
):
    df = store.load_latest_reports(filters)
    return ReportListResponse(
        total=len(df),
        page=filters.page,
        limit=filters.limit,
        pages=max(1, len(df) // filters.limit),
        data=df.to_dict(orient='records') if not df.empty else []
    )

@router.get("/latest", response_model=ReportListResponse)
def get_latest_reports(
    n: int = Query(100),
    store: ParquetStore = Depends(get_parquet_store)
):
    df = store.get_latest_n(n)
    return ReportListResponse(
        total=len(df),
        page=1,
        limit=n,
        pages=1,
        data=df.to_dict(orient='records') if not df.empty else []
    )

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(
    store: ParquetStore = Depends(get_parquet_store),
    cache: CacheManager = Depends(get_cache_manager)
):
    stats = store.get_statistics()
    return StatisticsResponse(**stats)

@router.get("/map", response_model=GeoFeatureCollection)
def get_map_data(
    store: ParquetStore = Depends(get_parquet_store)
):
    df = store.get_latest_n(5000) # Simplify for now
    features = []
    
    if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
        for idx, row in df.iterrows():
            if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(row['lon']), float(row['lat'])]
                    },
                    "properties": {
                        "id": None,
                        "tipo_delito": row.get('tipo_delito', 'DESCONOCIDO'),
                        "municipio": row.get('municipio'),
                        "departamento": row.get('departamento'),
                        "fecha": str(row.get('fecha', '')),
                        "fuente": "Datos Abiertos"
                    }
                })
                
    return GeoFeatureCollection(
        type='FeatureCollection',
        features=features,
        total=len(features)
    )

import pandas as pd
from utils.ai_advisor import AIAdvisor

@router.post("/chat", response_model=ChatResponse)
def chat_with_advisor(
    request: ChatRequest,
    store: ParquetStore = Depends(get_parquet_store)
):
    message = request.message.lower()
    
    # Very basic routing for the chatbot demonstration
    # In a real scenario we'd use an LLM or more complex NLP
    df = store.load_latest_reports(FilterParams(limit=10000))
    if df.empty:
        return ChatResponse(response="Actualmente no hay datos cargados en el sistema para realizar un diagnóstico.")
        
    advisor = AIAdvisor(df)
    
    if "mañana" in message or "riesgo" in message:
        risk_info = advisor.get_highest_risk_zone_tomorrow()
        response_text = f"Según el modelo predictivo, la zona de mayor riesgo para mañana es **{risk_info.get('zona')}** con un nivel **{risk_info.get('riesgo')}**. {risk_info.get('explicacion', '')}"
    elif "incremento" in message or "tendencia" in message or "subiendo" in message:
        trends = advisor.get_rising_crime_neighborhoods()
        if not trends:
            response_text = "Actualmente no detecto incrementos significativos recientes de más del 5% en ningún barrio."
        else:
            response_text = "He detectado las siguientes tendencias al alza:\n"
            for t in trends:
                response_text += f"- **{t['barrio']}**: incremento del {t['crecimiento_pct']:.1f}%\n"
    elif "hora" in message or "horario" in message or "pico" in message:
        hours_info = advisor.get_peak_crime_hours()
        if hours_info:
            response_text = f"La franja horaria más crítica se concentra entre las **{hours_info.get('rango_critico')}**. {hours_info.get('recomendacion', '')}"
        else:
            response_text = "No tengo suficientes datos para calcular horarios críticos."
    elif "recomendaciones" in message or "polic" in message or "despliegue" in message:
        recs = advisor.get_police_presence_recommendations()
        response_text = "Aquí están mis recomendaciones estratégicas:\n" + "\n".join(recs)
    else:
        response_text = "Soy el Asistente Predictivo de PIPAC. Puedo ayudarte con diagnósticos sobre: zonas de mayor riesgo para mañana, tendencias al alza por barrio, horarios críticos, o generar recomendaciones de despliegue policial. ¿Qué deseas consultar?"
        
    return ChatResponse(response=response_text)

