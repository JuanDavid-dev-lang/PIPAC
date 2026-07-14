"""API de denuncias ciudadanas con persistencia local o PostgreSQL/PostGIS."""

from __future__ import annotations

from functools import lru_cache
from math import asin, cos, radians, sin, sqrt
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(prefix="/api/v1/denuncias", tags=["Denuncias Ciudadanas"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATABASE = PROJECT_ROOT / "data" / "02_intermediate" / "pipac.db"


class DenunciaCreate(BaseModel):
    tipo_delito: str = Field(..., min_length=2, max_length=100)
    descripcion: str = Field(..., min_length=10, max_length=4000)
    ciudad: str = Field(..., min_length=2, max_length=120)
    departamento: Optional[str] = Field(default=None, max_length=120)
    barrio: Optional[str] = Field(default=None, max_length=160)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    es_anonima: bool = True
    nombre_denunciante: Optional[str] = Field(default=None, max_length=200)
    contacto: Optional[str] = Field(default=None, max_length=200)


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
    created_at: str


def _database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return configured_url

    LOCAL_DATABASE.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{LOCAL_DATABASE.as_posix()}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    database_url = _database_url()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
    if engine.dialect.name == "sqlite":
        _ensure_local_schema(engine)
    return engine


def _ensure_local_schema(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS denuncias_ciudadanas (
                    id_denuncia INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_delito TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    ciudad TEXT NOT NULL,
                    departamento TEXT,
                    barrio TEXT,
                    lat REAL,
                    lon REAL,
                    es_anonima BOOLEAN NOT NULL DEFAULT 1,
                    nombre_denunciante TEXT,
                    contacto TEXT,
                    estado TEXT NOT NULL DEFAULT 'RECIBIDA',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_denuncias_created "
                "ON denuncias_ciudadanas (created_at DESC)"
            )
        )


def _public_row(row: dict) -> dict:
    data = dict(row)
    if data.get("created_at") is not None:
        data["created_at"] = str(data["created_at"])
    if data.get("lat") is not None:
        data["lat"] = float(data["lat"])
    if data.get("lon") is not None:
        data["lon"] = float(data["lon"])
    return data


def _parameters(denuncia: DenunciaCreate) -> dict:
    return {
        "tipo": denuncia.tipo_delito.strip(),
        "desc": denuncia.descripcion.strip(),
        "ciudad": denuncia.ciudad.strip(),
        "dpto": denuncia.departamento.strip() if denuncia.departamento else None,
        "barrio": denuncia.barrio.strip() if denuncia.barrio else None,
        "lat": denuncia.lat,
        "lon": denuncia.lon,
        "anonima": denuncia.es_anonima,
        "nombre": denuncia.nombre_denunciante if not denuncia.es_anonima else None,
        "contacto": denuncia.contacto if not denuncia.es_anonima else None,
    }


@router.post("/", summary="Crear una denuncia ciudadana", response_model=DenunciaOut)
def crear_denuncia(denuncia: DenunciaCreate):
    engine = get_engine()
    params = _parameters(denuncia)
    try:
        with engine.begin() as conn:
            if engine.dialect.name == "postgresql":
                query = text(
                    """
                    INSERT INTO denuncias_ciudadanas
                        (tipo_delito, descripcion, ciudad, departamento, barrio,
                         lat, lon, geom, es_anonima, nombre_denunciante, contacto)
                    VALUES
                        (:tipo, :desc, :ciudad, :dpto, :barrio, :lat, :lon,
                         CASE WHEN :lat IS NOT NULL AND :lon IS NOT NULL
                              THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                              ELSE NULL END,
                         :anonima, :nombre, :contacto)
                    RETURNING id_denuncia, tipo_delito, descripcion, ciudad,
                              departamento, barrio, lat, lon, es_anonima, estado, created_at
                    """
                )
                row = conn.execute(query, params).mappings().one()
            else:
                result = conn.execute(
                    text(
                        """
                        INSERT INTO denuncias_ciudadanas
                            (tipo_delito, descripcion, ciudad, departamento, barrio,
                             lat, lon, es_anonima, nombre_denunciante, contacto)
                        VALUES
                            (:tipo, :desc, :ciudad, :dpto, :barrio,
                             :lat, :lon, :anonima, :nombre, :contacto)
                        """
                    ),
                    params,
                )
                row = conn.execute(
                    text(
                        """
                        SELECT id_denuncia, tipo_delito, descripcion, ciudad,
                               departamento, barrio, lat, lon, es_anonima, estado, created_at
                        FROM denuncias_ciudadanas
                        WHERE id_denuncia = :id
                        """
                    ),
                    {"id": result.lastrowid},
                ).mappings().one()
        return _public_row(dict(row))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="No fue posible guardar la denuncia. Intenta nuevamente.",
        ) from exc


@router.get("/", summary="Listar denuncias recientes", response_model=list[DenunciaOut])
def listar_denuncias(
    ciudad: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    filters = []
    params: dict = {"limit": limit}
    if ciudad:
        filters.append("LOWER(ciudad) = LOWER(:ciudad)")
        params["ciudad"] = ciudad
    if tipo:
        filters.append("LOWER(tipo_delito) = LOWER(:tipo)")
        params["tipo"] = tipo
    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    try:
        with get_engine().connect() as conn:
            rows = conn.execute(
                text(
                    f"""
                    SELECT id_denuncia, tipo_delito, descripcion, ciudad,
                           departamento, barrio, lat, lon, es_anonima, estado, created_at
                    FROM denuncias_ciudadanas
                    {where}
                    ORDER BY created_at DESC, id_denuncia DESC
                    LIMIT :limit
                    """
                ),
                params,
            ).mappings()
            return [_public_row(dict(row)) for row in rows]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="No fue posible consultar las denuncias.") from exc


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, (lat1, lon1, lat2, lon2))
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    value = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(value))


@router.get("/cercanas", summary="Denuncias cercanas a una ubicacion")
def denuncias_cercanas(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radio_km: float = Query(default=5.0, gt=0, le=200),
    limit: int = Query(default=10, ge=1, le=50),
):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                rows = conn.execute(
                    text(
                        """
                        SELECT id_denuncia, tipo_delito, descripcion, ciudad,
                               departamento, barrio, lat, lon, es_anonima, estado, created_at,
                               ROUND((ST_Distance(
                                   geom::geography,
                                   ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                               ) / 1000)::numeric, 2) AS distancia_km
                        FROM denuncias_ciudadanas
                        WHERE geom IS NOT NULL
                          AND ST_DWithin(
                              geom::geography,
                              ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                              :radio
                          )
                        ORDER BY distancia_km ASC
                        LIMIT :limit
                        """
                    ),
                    {"lat": lat, "lon": lon, "radio": radio_km * 1000, "limit": limit},
                ).mappings()
                return [_public_row(dict(row)) for row in rows]

            rows = conn.execute(
                text(
                    """
                    SELECT id_denuncia, tipo_delito, descripcion, ciudad,
                           departamento, barrio, lat, lon, es_anonima, estado, created_at
                    FROM denuncias_ciudadanas
                    WHERE lat IS NOT NULL AND lon IS NOT NULL
                    ORDER BY created_at DESC
                    """
                )
            ).mappings()
            nearby = []
            for row in rows:
                item = _public_row(dict(row))
                distance = _distance_km(lat, lon, item["lat"], item["lon"])
                if distance <= radio_km:
                    item["distancia_km"] = round(distance, 2)
                    nearby.append(item)
            nearby.sort(key=lambda item: item["distancia_km"])
            return nearby[:limit]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="No fue posible consultar denuncias cercanas.") from exc
