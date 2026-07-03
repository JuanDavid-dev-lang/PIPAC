from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["maintenance"])


@router.post("/datasets/refresh")
def refresh_datasets():
    return {"status": "queued"}


@router.post("/train")
def train_models():
    return {"status": "queued"}


@router.get("/export/{format_name}")
def export_results(format_name: str):
    if format_name not in {"csv", "json", "geojson"}:
        raise HTTPException(status_code=400, detail="Formato no soportado")
    return {"format": format_name, "status": "ready"}

