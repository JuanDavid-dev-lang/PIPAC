import logging
from typing import Any, Optional
import time

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, redis_url: Optional[str] = None, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._memory_cache = {}
        
    def get(self, key: str) -> Optional[Any]:
        if key in self._memory_cache:
            val, expiry = self._memory_cache[key]
            if time.time() < expiry:
                return val
            else:
                del self._memory_cache[key]
        return None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expiry = time.time() + (ttl if ttl else self.ttl_seconds)
        self._memory_cache[key] = (value, expiry)
        
    def invalidate(self, pattern: str):
        keys_to_del = []
        # Basic prefix matching
        prefix = pattern.replace('*', '')
        for k in self._memory_cache.keys():
            if k.startswith(prefix):
                keys_to_del.append(k)
        for k in keys_to_del:
            del self._memory_cache[k]
