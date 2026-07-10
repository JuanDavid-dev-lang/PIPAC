from functools import lru_cache
from pathlib import Path
from ..loader.parquet_store import ParquetStore
from ..cache.cache_manager import CacheManager

PROJECT_ROOT = Path(__file__).resolve().parents[4]

@lru_cache()
def get_parquet_store() -> ParquetStore:
    return ParquetStore(PROJECT_ROOT)

@lru_cache()
def get_cache_manager() -> CacheManager:
    return CacheManager()
