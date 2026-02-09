import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0


class TechniqueResultCache:
    """In-memory technique result cache with content-hash invalidation.

    Uses in-memory dict for simplicity (no MongoDB dependency for cache).
    TTL-based automatic expiration.
    """

    def __init__(self, ttl_hours: int = 24):
        self._cache: dict[str, dict] = {}
        self._ttl = timedelta(hours=ttl_hours)
        self._stats = CacheStats()

    @staticmethod
    def compute_content_hash(repo_url: str, repo_context: dict) -> str:
        """Generate content hash from repo URL + key content fields."""
        content = repo_url
        content += repo_context.get("readme", "")[:1000]
        file_tree = sorted(repo_context.get("file_tree", []))[:100]
        content += json.dumps(file_tree)
        content += json.dumps(sorted(repo_context.get("languages", {}).items()))
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _make_key(self, technique_id: str, repo_url: str, content_hash: str) -> str:
        return f"{technique_id}:{repo_url}:{content_hash}"

    def get(
        self, technique_id: str, repo_url: str, content_hash: str
    ) -> Optional[dict]:
        key = self._make_key(technique_id, repo_url, content_hash)
        entry = self._cache.get(key)
        if entry is None:
            self._stats.misses += 1
            return None
        if datetime.now(timezone.utc) - entry["created_at"] > self._ttl:
            del self._cache[key]
            self._stats.misses += 1
            return None
        self._stats.hits += 1
        result = entry["result"].copy()
        result["from_cache"] = True
        return result

    def set(
        self,
        technique_id: str,
        repo_url: str,
        content_hash: str,
        result: dict,
    ) -> None:
        key = self._make_key(technique_id, repo_url, content_hash)
        self._cache[key] = {
            "result": result,
            "created_at": datetime.now(timezone.utc),
            "technique_id": technique_id,
            "repo_url": repo_url,
            "content_hash": content_hash,
        }

    def invalidate(self, repo_url: str) -> int:
        keys_to_remove = [k for k in self._cache if f":{repo_url}:" in k]
        for k in keys_to_remove:
            del self._cache[k]
        return len(keys_to_remove)

    def stats(self) -> CacheStats:
        total = self._stats.hits + self._stats.misses
        self._stats.total_entries = len(self._cache)
        self._stats.hit_rate = self._stats.hits / total if total > 0 else 0.0
        return self._stats

    def clear(self) -> None:
        self._cache.clear()
        self._stats = CacheStats()


_cache_instance: Optional[TechniqueResultCache] = None


def get_technique_cache() -> TechniqueResultCache:
    global _cache_instance
    if _cache_instance is None:
        from app.core.config import settings

        _cache_instance = TechniqueResultCache(
            ttl_hours=settings.TECHNIQUE_CACHE_TTL_HOURS
        )
    return _cache_instance
