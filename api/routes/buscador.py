from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd
from fastapi import APIRouter, Query


router = APIRouter(prefix="/api/v1/buscador", tags=["Buscador Avanzado Nacional"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENTITY_CATALOG = [
    {
        "id": "policia-nacional",
        "tipo": "entidad",
        "titulo": "Policia Nacional de Colombia",
        "subtitulo": "Linea de emergencias 123",
        "departamento": "NACIONAL",
        "municipio": "NACIONAL",
        "categoria": "Seguridad",
    },
    {
        "id": "alcaldia-bucaramanga",
        "tipo": "entidad",
        "titulo": "Alcaldia de Bucaramanga",
        "subtitulo": "Atencion ciudadana y tramites municipales",
        "departamento": "SANTANDER",
        "municipio": "BUCARAMANGA",
        "categoria": "Gubernamental",
    },
    {
        "id": "alcaldia-bogota",
        "tipo": "entidad",
        "titulo": "Alcaldia Mayor de Bogota",
        "subtitulo": "Servicios y tramites distritales",
        "departamento": "BOGOTA D.C.",
        "municipio": "BOGOTA D.C.",
        "categoria": "Gubernamental",
    },
    {
        "id": "fiscalia-general",
        "tipo": "entidad",
        "titulo": "Fiscalia General de la Nacion",
        "subtitulo": "Denuncias y orientacion ciudadana",
        "departamento": "NACIONAL",
        "municipio": "NACIONAL",
        "categoria": "Justicia",
    },
]


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(character for character in text if not unicodedata.combining(character)).upper()


def _matches_filter(value: str, expected: str | None) -> bool:
    return not expected or _normalize(value) == _normalize(expected)


def _catalog_results(
    query: str,
    departamento: str | None,
    municipio: str | None,
    categoria: str | None,
) -> list[dict]:
    results = []
    for item in ENTITY_CATALOG:
        searchable = " ".join(str(value) for value in item.values())
        if query not in _normalize(searchable):
            continue
        if not _matches_filter(item["departamento"], departamento):
            continue
        if not _matches_filter(item["municipio"], municipio):
            continue
        if not _matches_filter(item["categoria"], categoria):
            continue
        results.append(item.copy())
    return results


def _territory_results(
    query: str,
    departamento: str | None,
    municipio: str | None,
    categoria: str | None,
) -> list[dict]:
    if categoria and _normalize(categoria) not in {"TERRITORIO", "SEGURIDAD"}:
        return []

    data_path = PROJECT_ROOT / "datasets" / "processed" / "crime_hurtos_nacional.parquet"
    if not data_path.exists():
        return []

    try:
        df = pd.read_parquet(data_path, columns=["departamento", "municipio"])
    except (OSError, ValueError, KeyError):
        return []

    df = df.dropna(subset=["departamento", "municipio"]).copy()
    normalized_department = df["departamento"].map(_normalize)
    normalized_municipality = df["municipio"].map(_normalize)
    mask = normalized_department.str.contains(query, regex=False) | normalized_municipality.str.contains(
        query, regex=False
    )
    if departamento:
        mask &= normalized_department == _normalize(departamento)
    if municipio:
        mask &= normalized_municipality == _normalize(municipio)

    grouped = (
        df.loc[mask]
        .groupby(["departamento", "municipio"], dropna=False)
        .size()
        .reset_index(name="total_eventos")
        .sort_values("total_eventos", ascending=False)
    )
    return [
        {
            "id": f"territorio-{index}",
            "tipo": "territorio",
            "titulo": str(row["municipio"]),
            "subtitulo": f'{row["departamento"]} - {int(row["total_eventos"])} eventos registrados',
            "departamento": str(row["departamento"]),
            "municipio": str(row["municipio"]),
            "categoria": "Territorio",
        }
        for index, (_, row) in enumerate(grouped.iterrows())
    ]


@router.get("/", summary="Busqueda global con filtros")
def buscar(
    q: str = Query(..., min_length=2, max_length=100),
    departamento: str | None = None,
    municipio: str | None = None,
    categoria: str | None = None,
    limit: int = Query(default=10, ge=1, le=30),
):
    query = _normalize(q.strip())
    results = _catalog_results(query, departamento, municipio, categoria)
    results.extend(_territory_results(query, departamento, municipio, categoria))
    unique_results = {item["id"]: item for item in results}
    limited_results = list(unique_results.values())[:limit]
    return {"resultados": limited_results, "total": len(unique_results), "query": q}
