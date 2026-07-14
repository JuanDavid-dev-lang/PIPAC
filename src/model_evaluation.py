from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def load_model_metrics(models_dir: str | Path = "models") -> dict[str, dict[str, Any]]:
    """Carga los archivos `*.metrics.json` generados durante entrenamiento."""
    metrics: dict[str, dict[str, Any]] = {}
    for path in Path(models_dir).glob("*.metrics.json"):
        with path.open("r", encoding="utf-8") as file:
            metrics[path.stem.replace(".metrics", "")] = json.load(file)
    return metrics


__all__ = ["load_model_metrics"]
