from __future__ import annotations

from pathlib import Path

import joblib


def test_serialized_model_artifacts_are_present():
    model_paths = list(Path("models").glob("*.joblib"))
    assert model_paths, "No se encontraron modelos serializados en models/."


def test_first_model_artifact_can_be_loaded():
    model_path = next(Path("models").glob("*.joblib"))
    model = joblib.load(model_path)
    assert model is not None
