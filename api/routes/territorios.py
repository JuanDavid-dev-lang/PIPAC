from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/territorios", tags=["Territorios Nacionales"])

@router.get("/departamentos", summary="Obtener todos los departamentos")
def get_departamentos():
    # TODO: Implementar consulta a la base de datos real
    return {"departamentos": [{"id_departamento": "11", "nombre": "BOGOTÁ, D.C."}, {"id_departamento": "05", "nombre": "ANTIOQUIA"}]}

@router.get("/municipios", summary="Obtener municipios por departamento")
def get_municipios(departamento_id: str = None):
    # TODO: Implementar consulta a la base de datos real
    return {"municipios": [{"id_municipio": "11001", "nombre": "BOGOTÁ, D.C.", "id_departamento": "11"}]}
