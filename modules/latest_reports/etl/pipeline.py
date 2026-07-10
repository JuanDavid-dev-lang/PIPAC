import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from typing import List, Optional

from .socrata_fetcher import SocrataFetcher
from .cleaner import DataCleaner
from .normalizer import TerritorialNormalizer
from ..config import NATIONAL_DATASETS

logger = logging.getLogger(__name__)

class LatestReportsPipeline:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.raw_dir = self.project_root / 'datasets' / 'raw'
        self.processed_dir = self.project_root / 'datasets' / 'processed'
        self.cache_dir = self.project_root / 'datasets' / 'cache'
        self.featured_dir = self.project_root / 'datasets' / 'featured'
        
        for d in [self.raw_dir, self.processed_dir, self.cache_dir, self.featured_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        self.cleaner = DataCleaner()
        self.normalizer = TerritorialNormalizer()

    def run_full(self, dataset_keys: Optional[List[str]] = None) -> dict:
        keys_to_run = dataset_keys if dataset_keys else list(NATIONAL_DATASETS.keys())
        results = {}
        
        def _process_one(key):
            try:
                logger.info(f"Starting full pipeline for {key}")
                dataset_info = NATIONAL_DATASETS[key]
                fetcher = SocrataFetcher(dataset_info['id'])
                df = fetcher.fetch_all(limit=10000) # smaller limit for testing
                
                # Cleaning
                df_clean = self.cleaner.clean(df, key)
                
                # Normalizing
                if 'departamento' in df_clean.columns:
                    norm_depts = df_clean['departamento'].apply(self.normalizer.normalize_departamento)
                    df_clean['departamento'] = norm_depts.apply(lambda x: x[0])
                    df_clean['codigo_dane_depto'] = norm_depts.apply(lambda x: x[1])
                
                if 'municipio' in df_clean.columns:
                    norm_mpios = df_clean.apply(lambda row: self.normalizer.normalize_municipio(row['municipio'], row.get('departamento')), axis=1)
                    df_clean['municipio'] = norm_mpios.apply(lambda x: x[0])
                    df_clean['codigo_dane'] = norm_mpios.apply(lambda x: x[1])
                    
                    if 'lat' not in df_clean.columns:
                        df_clean['lat'] = None
                    if 'lon' not in df_clean.columns:
                        df_clean['lon'] = None
                        
                    missing_coords = df_clean['lat'].isna() | df_clean['lon'].isna()
                    if missing_coords.any():
                        coords = df_clean.loc[missing_coords, 'municipio'].apply(self.normalizer.get_centroid)
                        df_clean.loc[missing_coords, 'lat'] = coords.apply(lambda x: x[0])
                        df_clean.loc[missing_coords, 'lon'] = coords.apply(lambda x: x[1])
                        
                # Save
                self._save_datasets(df_clean, key)
                return True
            except Exception as e:
                logger.error(f"Error processing {key}: {e}")
                return False

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_key = {executor.submit(_process_one, key): key for key in keys_to_run}
            for future in future_to_key:
                key = future_to_key[future]
                results[key] = future.result()
                
        return results

    def _save_datasets(self, df: pd.DataFrame, dataset_key: str):
        if df.empty:
            return
        
        raw_path = self.raw_dir / f"{dataset_key}.csv"
        processed_path = self.processed_dir / f"{dataset_key}.parquet"
        
        df.to_csv(raw_path, index=False)
        df.to_parquet(processed_path, index=False)
        logger.info(f"Saved dataset {dataset_key} to {processed_path}")
