"""
Router de Denuncias Ciudadanas — PIPAC V2
Permite crear y consultar reportes ciudadanos almacenados en PostgreSQL.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os
from sqlalchemy import create_engine, text

router = APIRouter(prefix="/api/v1/denuncias", tags=["Denuncias Ciudadanas"])

DB_URL = os.getenv("DATABASE_URL", "postgresql://crime:crime@localhost:5432/crime_ai")

def get_engine():
    return create_engine(DB_URL)

# ─── Modelos Pydantic ─────────────────────────────────────────────────────────

class DenunciaCreate(BaseModel):
    tipo_delito: str = Field(..., description="Robo, Homicidio, Extorsión, Acoso, Otro")
    descripcion: str = Field(..., min_length=10, description="Descripción del hecho")
    ciudad: str = Field(..., description="Ciudad donde ocurrió")
    departamento: Optional[str] = None
    barrio: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    es_anonima: bool = True
    nombre_denunciante: Optional[str] = None
    contacto: Optional[str] = None  # email o teléfono

class DenunciaOut(BaseModel):
    id_denuncia: int
    tipo_delito: str
    descripcion: str
    ciudad: str
    departamento: Optional[str]
    barrio: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    es_anonima: bool
    estado: str
    created_at: datetime

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", summary="Crear una denuncia ciudadana", response_model=DenunciaOut)
def crear_denuncia(denuncia: DenunciaCreate):
    """Guarda una denuncia ciudadana en PostgreSQL."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO denuncias_ciudadanas
                        (tipo_delito, descripcion, ciudad, departamento, barrio,
                         lat, lon, geom, es_anonima, nombre_denunciante, contacto)
                    VALUES
                        (:tipo, :desc, :ciudad, :dpto, :barrio,
                         :lat, :lon,
                         CASE WHEN :lat IS NOT NULL AND :lon IS NOT NULL
                              THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                              ELSE NULL END,
                         :anonima, :nombre, :contacto)
                    RETURNING id_denuncia, tipo_delito, descripcion, ciudad,
                              departamento, barrio, lat, lon, es_anonima, estado, created_at
                """),
                {
                    "tipo": denuncia.tipo_delito,
                    "desc": denuncia.descripcion,
                    "ciudad": denuncia.ciudad,
                    "dpto": denuncia.departamento,
                    "barrio": denuncia.barrio,
                    "lat": denuncia.lat,
                    "lon": denuncia.lon,
                    "anonima": denuncia.es_anonima,
                    "nombre": denuncia.nombre_denunciante if not denuncia.es_anonima else None,
                    "contacto": denuncia.contacto if not denuncia.es_anonima else None,
                }
            )
            row = result.mappings().fetchone()
            return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar denuncia: {str(e)}")


@router.get("/", summary="Listar denuncias recientes", response_model=List[DenunciaOut])
def listar_denuncias(
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de delito"),
    limit: int = Query(20, le=100),
):
    """Lista las últimas denuncias ciudadanas registradas."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            filters = []
            params: dict = {"limit": limit}
            if ciudad:
                filters.append("LOWER(ciudad) = LOWER(:ciudad)")
                params["ciudad"] = ciudad
            if tipo:
                filters.append("LOWER(tipo_delito) = LOWER(:tipo)")
                params["tipo"] = tipo

            where = ("WHERE " + " AND ".join(filters)) if filters else ""
            result = conn.execute(
                text(f"""
                    SELECT id_denuncia, tipo_delito, descripcion, ciudad,
                           departamento, barrio, lat, lon, es_anonima, estado, created_at
                    FROM denuncias_ciudadanas
                    {where}
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                params
            )
            return [dict(r) for r in result.mappings()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {str(e)}")


@router.get("/cercanas", summary="Denuncias cercanas a una ubicación")
def denuncias_cercanas(
    lat: float = Query(...),
    lon: float = Query(...),
    radio_km: float = Query(5.0, description="Radio en kilómetros"),
    limit: int = Query(10, le=50),
):
    """Retorna las denuncias más cercanas a unas coordenadas dadas."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id_denuncia, tipo_delito, descripcion, ciudad, barrio,
                           lat, lon, es_anonima, estado, created_at,
                           ROUND(
                             ST_Distance(
                               geom::geography,
                               ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                             ) / 1000, 2
                           ) AS distancia_km
                    FROM denuncias_ciudadanas
                    WHERE geom IS NOT NULL
                      AND ST_DWithin(
                            geom::geography,
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                            :radio
                          )
                    ORDER BY distancia_km ASC
                    LIMIT :limit
                """),
                {"lat": lat, "lon": lon, "radio": radio_km * 1000, "limit": limit}
            )
            return [dict(r) for r in result.mappings()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error espacial: {str(e)}")
