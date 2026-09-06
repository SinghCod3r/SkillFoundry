from __future__ import annotations

import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def make_cache_key(*parts: str) -> str:
    """Create a stable cache key from multiple parts."""
    h = hashlib.sha256()
    for part in parts:
        h.update(str(part).encode('utf-8'))
    return h.hexdigest()

class Cache:
    """File-based cache with versioned keys."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        safe_key = hashlib.sha256(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[str]:
        """Return cached value or None if expired/missing."""
        path = self._get_path(key)
        if not path.exists():
            return None
            
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            ttl = data.get('ttl')
            created_at = data.get('created_at')
            
            if ttl is not None and created_at is not None:
                if time.time() > created_at + ttl:
                    path.unlink(missing_ok=True)
                    return None
                    
            logger.info("Using cached result")
            return data.get('value')
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Store value with optional TTL in seconds."""
        path = self._get_path(key)
        data = {
            'value': value,
            'created_at': time.time(),
            'ttl': ttl
        }
        
        try:
            path.write_text(json.dumps(data), encoding='utf-8')
        except OSError as e:
            logger.error(f"Failed to write cache key {key}: {e}")

    def has(self, key: str) -> bool:
        """Check if a valid key exists in cache."""
        return self.get(key) is not None

    def delete(self, key: str) -> None:
        """Delete a cache entry."""
        path = self._get_path(key)
        path.unlink(missing_ok=True)

    def clear(self) -> None:
        """Delete all cache entries."""
        for path in self.cache_dir.glob("*.json"):
            path.unlink(missing_ok=True)
