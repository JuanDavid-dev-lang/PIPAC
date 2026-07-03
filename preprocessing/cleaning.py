from __future__ import annotations

import re
import unicodedata

import pandas as pd


def normalize_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text)
    return text


def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [normalize_text(col).lower() if col else col for col in cleaned.columns]
    for column in cleaned.select_dtypes(include="object").columns:
        cleaned[column] = cleaned[column].map(normalize_text)
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.replace({"": None, "NA": None, "N/A": None, "NULL": None})
    return cleaned

