from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config.settings import DATASETS
from preprocessing.cleaning import standardize_dataframe
from preprocessing.features import build_temporal_features
from utils.socrata_client import fetch_socrata_csv


@dataclass
class ETLResult:
    dataset_name: str
    rows: int
    raw_path: Path
    processed_path: Path


class CrimeETL:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.raw_dir = project_root / "datasets" / "raw"
        self.processed_dir = project_root / "datasets" / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, dataset_key: str) -> pd.DataFrame:
        dataset = DATASETS[dataset_key]
        return fetch_socrata_csv(dataset["id"])

    def transform(self, df: pd.DataFrame, dataset_key: str) -> pd.DataFrame:
        data = standardize_dataframe(df)
        
        if dataset_key == "crime_bga":
            # Bucaramanga crime: columns are barrios_hecho, fecha_hecho (YYYY-MM-DDThh:mm:ss.000), hora_hecho, descripcion_conducta
            # Combine fecha_hecho and hora_hecho to create a proper datetime
            if "fecha_hecho" in data.columns:
                # Extraer la fecha simple (YYYY-MM-DD)
                data["fecha_clean"] = data["fecha_hecho"].str.split("T").str[0]
                if "hora_hecho" in data.columns:
                    # Rellenar horas a formato HH:MM:00 si es necesario
                    data["hora_clean"] = data["hora_hecho"].astype(str).str.strip()
                    # Si no contiene ':', asumimos medianoche o formato crudo
                    data.loc[~data["hora_clean"].str.contains(":", na=False), "hora_clean"] = "00:00"
                    data["fecha_hora"] = pd.to_datetime(data["fecha_clean"] + " " + data["hora_clean"], errors="coerce")
                else:
                    data["fecha_hora"] = pd.to_datetime(data["fecha_clean"], errors="coerce")
            
            data["tipo_delito"] = data["descripcion_conducta"]
            data["barrio"] = data["barrios_hecho"]
            data["comuna"] = data["nom_com"]
            data["zona_tipo"] = data["localidad"]
            data["conteo"] = data["cantidad_unica"].fillna(1).astype(int)
            
        elif dataset_key == "accidentes_bga":
            if "fecha" in data.columns:
                data["fecha_clean"] = data["fecha"].str.split("T").str[0]
                if "hora" in data.columns:
                    data["hora_clean"] = data["hora"].astype(str).str.strip()
                    data.loc[~data["hora_clean"].str.contains(":", na=False), "hora_clean"] = "00:00"
                    data["fecha_hora"] = pd.to_datetime(data["fecha_clean"] + " " + data["hora_clean"], errors="coerce")
                else:
                    data["fecha_hora"] = pd.to_datetime(data["fecha_clean"], errors="coerce")
            data["barrio"] = data["barrio"]
            data["comuna"] = data["nombrecomuna"]
            
        elif dataset_key == "crime_hurtos_nacional":
            if "fecha_hecho" in data.columns:
                data["fecha_clean"] = data["fecha_hecho"].str.split("T").str[0]
                data["fecha_hora"] = pd.to_datetime(data["fecha_clean"], errors="coerce")
            data["tipo_delito"] = data["tipo_de_hurto"]
            data["barrio"] = data["municipio"] # A nivel nacional, representamos la granularidad geográfica principal por el municipio
            data["comuna"] = data["departamento"]
            data["conteo"] = data["cantidad"].fillna(1).astype(int)

            
        # Generar variables temporales principales si existe fecha_hora
        if "fecha_hora" in data.columns:
            data = build_temporal_features(data, "fecha_hora")
            
        data = data.dropna(how="all")
        return data

    def load_local(self, df: pd.DataFrame, dataset_key: str) -> ETLResult:
        raw_path = self.raw_dir / f"{dataset_key}.csv"
        processed_path = self.processed_dir / f"{dataset_key}.parquet"
        
        # En caso de error, guardamos directo, si no, guardamos raw original y processed transformado
        if not raw_path.exists() and "error" not in df.columns:
            # Guardamos un archivo simulado o temporal
            df.head(100).to_csv(raw_path, index=False)
            
        df.to_parquet(processed_path, index=False)
        return ETLResult(dataset_key, len(df), raw_path, processed_path)

    def run(self, dataset_key: str) -> ETLResult:
        raw = self.extract(dataset_key)
        processed = self.transform(raw, dataset_key)
        return self.load_local(processed, dataset_key)

    def split_national_by_municipio(self, dataset_key: str = "crime_hurtos_nacional") -> list[ETLResult]:
        """Procesa el dataset nacional y escribe parquet individuales por municipio.

        Esto facilita servir datos por ciudad desde la API (crime_{municipio}.parquet).
        """
        raw = self.extract(dataset_key)
        processed = self.transform(raw, dataset_key)
        results: list[ETLResult] = []
        if "municipio" not in processed.columns:
            # Si no hay columna municipio, guardamos el dataset tal cual
            results.append(self.load_local(processed, dataset_key))
            return results

        # Agrupar por municipio y guardar por separado
        for municipio, grp in processed.groupby(processed["municipio"].astype(str)):
            key_safe = municipio.lower().replace(" ", "_")
            fname = f"crime_{key_safe}.parquet"
            processed_path = self.processed_dir / fname
            try:
                grp.to_parquet(processed_path, index=False)
                results.append(ETLResult(fname, len(grp), self.raw_dir / f"{dataset_key}.csv", processed_path))
            except Exception:
                # en caso de fallo, seguimos con los demas
                continue
        return results


def run_default_etl(project_root: str | Path, split_national: bool = False) -> list[ETLResult]:
    etl = CrimeETL(Path(project_root))
    results: list[ETLResult] = []
    for key in ("crime_bga", "crime_hurtos_nacional", "poblacion_bga", "accidentes_bga"):
        try:
            results.append(etl.run(key))
        except Exception as exc:
            fallback = pd.DataFrame({"dataset": [key], "error": [str(exc)]})
            results.append(etl.load_local(fallback, f"{key}_error"))

    # Si se solicita, dividir el dataset nacional por municipio
    if split_national:
        try:
            split_results = etl.split_national_by_municipio("crime_hurtos_nacional")
            results.extend(split_results)
        except Exception:
            pass

    return results


