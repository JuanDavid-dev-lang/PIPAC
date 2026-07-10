from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class ReportItem(BaseModel):
    id: Optional[int] = None
    external_id: Optional[str] = None
    fecha: Optional[datetime] = None
    hora: Optional[int] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    codigo_dane: Optional[str] = None
    barrio: Optional[str] = None
    comuna: Optional[str] = None
    zona: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    tipo_delito: str = "DESCONOCIDO"
    modalidad: Optional[str] = None
    arma: Optional[str] = None
    victimas: Optional[int] = None
    sexo: Optional[str] = None
    edad: Optional[int] = None
    grupo_etario: Optional[str] = None
    estado: Optional[str] = None
    fuente: str = "DESCONOCIDO"
    ultima_actualizacion: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ReportListResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    data: List[ReportItem]

class StatisticsResponse(BaseModel):
    total_denuncias: int
    denuncias_hoy: int
    denuncias_24h: int
    denuncias_7d: int
    denuncias_30d: int
    variacion_semanal: float
    variacion_mensual: float
    top_departamentos: List[dict]
    top_municipios: List[dict]
    top_barrios: List[dict]
    top_delitos: List[dict]
    top_modalidades: List[dict]
    ultima_denuncia: Optional[datetime] = None
    fuentes: List[str]

class GeoFeatureProperties(BaseModel):
    id: Optional[int] = None
    tipo_delito: str = "DESCONOCIDO"
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    fecha: Optional[str] = None
    modalidad: Optional[str] = None
    arma: Optional[str] = None
    fuente: str = "DESCONOCIDO"

class GeoFeature(BaseModel):
    type: str = 'Feature'
    geometry: dict
    properties: GeoFeatureProperties

class GeoFeatureCollection(BaseModel):
    type: str = 'FeatureCollection'
    features: List[GeoFeature]
    total: int

class TimelinePoint(BaseModel):
    periodo: str
    conteo: int
    tipo_delito: Optional[str] = None

class TimelineResponse(BaseModel):
    granularity: str
    data: List[TimelinePoint]

class FilterParams(BaseModel):
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    barrio: Optional[str] = None
    comuna: Optional[str] = None
    tipo_delito: Optional[str] = None
    modalidad: Optional[str] = None
    arma: Optional[str] = None
    sexo: Optional[str] = None
    edad_min: Optional[int] = None
    edad_max: Optional[int] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    zona: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    limit: int = 50
    sort_by: str = 'fecha'
    order: str = 'desc'

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
