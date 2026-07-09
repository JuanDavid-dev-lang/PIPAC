from __future__ import annotations

import requests
from typing import Any


def fetch_crimes(api_base: str = "http://127.0.0.1:8000", **params) -> list[dict[str, Any]]:
    """Consume el endpoint /api/v1/crimes y devuelve la lista de items.

    params: city, department, municipio, limit
    """
    url = f"{api_base.rstrip('/')}/api/v1/crimes"
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        return payload.get("items", [])
    except Exception:
        return []


def fetch_predictions(api_base: str = "http://127.0.0.1:8000", city: str | None = None, target_date: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    url = f"{api_base.rstrip('/')}/api/v1/predictions"
    params: dict[str, Any] = {"limit": limit}
    if city:
        params["city"] = city
    if target_date:
        params["target_date"] = target_date
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        return payload.get("predictions", [])
    except Exception:
        return []
