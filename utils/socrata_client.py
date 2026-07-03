from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
import requests

from config.settings import settings


def _headers() -> dict[str, str]:
    if settings.socrata_app_token:
        return {"X-App-Token": settings.socrata_app_token}
    return {}


def fetch_socrata_csv(dataset_id: str, where: str | None = None, limit: int = 50000) -> pd.DataFrame:
    url = f"{settings.socrata_base_url}/{dataset_id}.csv"
    params: dict[str, Any] = {"$limit": limit}
    if where:
        params["$where"] = where
    response = requests.get(url, params=params, headers=_headers(), timeout=120)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))


def fetch_socrata_json(dataset_id: str, where: str | None = None, limit: int = 50000) -> list[dict[str, Any]]:
    url = f"{settings.socrata_base_url}/{dataset_id}.json"
    params: dict[str, Any] = {"$limit": limit}
    if where:
        params["$where"] = where
    response = requests.get(url, params=params, headers=_headers(), timeout=120)
    response.raise_for_status()
    return response.json()

