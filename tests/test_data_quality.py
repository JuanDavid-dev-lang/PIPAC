from __future__ import annotations

from pathlib import Path

import pandas as pd

from preprocessing.cleaning import standardize_dataframe
from preprocessing.features import build_temporal_features


def test_standardize_dataframe_normalizes_columns_and_values():
    df = pd.DataFrame({" Municipio ": ["Bogota", "Bogota"], "Valor": [" A ", " A "]})
    cleaned = standardize_dataframe(df)

    assert list(cleaned.columns) == ["municipio", "valor"]
    assert cleaned.iloc[0]["municipio"] == "BOGOTA"
    assert len(cleaned) == 1


def test_temporal_features_are_created():
    df = pd.DataFrame({"fecha_hora": ["2026-01-15 18:30:00"]})
    featured = build_temporal_features(df)

    assert featured.loc[0, "anio"] == 2026
    assert featured.loc[0, "mes"] == 1
    assert featured.loc[0, "hora"] == 18


def test_raw_data_directory_exists():
    assert Path("data/01_raw").exists()
