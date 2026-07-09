from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/entidades", tags=["Entidades y Servicios"])

@router.get("/", summary="Obtener entidades")
def get_entidades(municipio_id: str = None, categoria_id: int = None):
    # TODO: Implementar consulta real
    return {"entidades": []}

@router.get("/{entidad_id}", summary="Detalle de entidad")
def get_entidad_detalle(entidad_id: int):
    # TODO: Implementar consulta real
    return {"id_entidad": entidad_id, "nombre": "Entidad Oficial Mock", "descripcion": "Descripción detallada", "horarios": [], "telefonos": [], "enlaces": []}

@router.get("/{entidad_id}/tramites", summary="Trámites de la entidad")
def get_tramites(entidad_id: int):
    # TODO: Implementar consulta real
    return {"tramites": []}
