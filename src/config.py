from __future__ import annotations

from pathlib import Path

from config.settings import DATASETS, settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "01_raw"
INTERMEDIATE_DATA_DIR = DATA_DIR / "02_intermediate"
PRIMARY_DATA_DIR = DATA_DIR / "03_primary"
MODEL_OUTPUT_DIR = DATA_DIR / "04_model_output"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"


__all__ = [
    "DATASETS",
    "settings",
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "INTERMEDIATE_DATA_DIR",
    "PRIMARY_DATA_DIR",
    "MODEL_OUTPUT_DIR",
    "MODELS_DIR",
    "REPORTS_DIR",
]
