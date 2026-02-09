"""Tests for TechniqueResultCache.

These tests cover cache operations, TTL expiration, invalidation,
content hash computation, and statistics tracking.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.techniques.cache import (
    CacheStats,
    TechniqueResultCache,
    get_technique_cache,
)


@pytest.fixture
def cache():
    """Fixture providing a fresh TechniqueResultCache instance."""
    return TechniqueResultCache(ttl_hours=24)


@pytest.fixture
def sample_repo_context():
    """Fixture providing sample repository context."""
    return {
        "readme": "# Test Repository\n\nThis is a test readme.",
        "file_tree": ["src/main.py", "README.md", "tests/test.py"],
        "languages": {"Python": 1000, "Markdown": 200},
    }


@pytest.fixture
def sample_result():
    """Fixture providing sample technique result."""
    return {
        "score": 85,
        "confidence": "high",
        "details": {"complexity": "medium"},
    }


class TestCacheBasicOperations:
    """Test basic cache get/set operations."""

    def test_cache_miss_returns_none(self, cache):
        """Cache miss should return None."""
        result = cache.get("tech_1", "https://github.com/user/repo", "hash123")
        assert result is None

    def test_cache_set_then_get_returns_result(self, cache, sample_result):
        """Setting then getting should return result with from_cache=True."""
        cache.set(
            "tech_1",
            "https://github.com/user/repo",
            "hash123",
            sample_result,
        )
        result = cache.get("tech_1", "https://github.com/user/repo", "hash123")
        assert result is not None
        assert result["score"] == 85
        assert result["confidence"] == "high"
        assert result["from_cache"] is True

    def test_different_content_hash_cache_miss(self, cache, sample_result):
        """Different content hash should result in cache miss."""
        cache.set(
            "tech_1",
            "https://github.com/user/repo",
            "hash123",
            sample_result,
        )
        result = cache.get("tech_1", "https://github.com/user/repo", "different_hash")
        assert result is None


class TestCacheTTLExpiration:
    """Test TTL-based cache expiration."""

    def test_ttl_expiration_returns_none(self, cache, sample_result):
        """Expired entries should return None and be removed."""
        cache.set(
            "tech_1",
            "https://github.com/user/repo",
            "hash123",
            sample_result,
        )
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        cache_key = "tech_1:https://github.com/user/repo:hash123"
        cache._cache[cache_key]["created_at"] = old_time
        result = cache.get("tech_1", "https://github.com/user/repo", "hash123")
        assert result is None
        assert cache_key not in cache._cache


class TestCacheInvalidation:
    """Test cache invalidation by repo URL."""

    def test_invalidate_clears_entries_for_repo(self, cache, sample_result):
        """Invalidating a repo URL should clear all its entries."""
        repo_url = "https://github.com/user/repo"
        cache.set("tech_1", repo_url, "hash1", sample_result)
        cache.set("tech_2", repo_url, "hash2", sample_result)
        cache.set("tech_1", "https://github.com/user/other", "hash3", sample_result)
        count = cache.invalidate(repo_url)
        assert count == 2
        assert cache.get("tech_1", repo_url, "hash1") is None
        assert cache.get("tech_2", repo_url, "hash2") is None
        assert cache.get("tech_1", "https://github.com/user/other", "hash3") is not None

    def test_invalidate_does_not_affect_other_repos(self, cache, sample_result):
        """Invalidating one repo should not affect other repos."""
        repo1 = "https://github.com/user/repo1"
        repo2 = "https://github.com/user/repo2"
        cache.set("tech_1", repo1, "hash1", sample_result)
        cache.set("tech_1", repo2, "hash2", sample_result)
        cache.invalidate(repo1)
        assert cache.get("tech_1", repo2, "hash2") is not None


class TestCacheStats:
    """Test cache statistics tracking."""

    def test_stats_tracking_accurate(self, cache, sample_result):
        """Stats should accurately track hits, misses, and hit rate."""
        repo_url = "https://github.com/user/repo"
        cache.set("tech_1", repo_url, "hash1", sample_result)
        cache.get("tech_1", repo_url, "hash1")
        cache.get("tech_1", repo_url, "hash1")
        cache.get("tech_1", repo_url, "missing_hash")
        stats = cache.stats()
        assert stats.hits == 2
        assert stats.misses == 1
        assert stats.hit_rate == 2 / 3
        assert stats.total_entries == 1

    def test_stats_with_no_accesses(self, cache):
        """Stats with no accesses should have zero hit rate."""
        stats = cache.stats()
        assert stats.hit_rate == 0.0
        assert stats.hits == 0
        assert stats.misses == 0


class TestContentHashComputation:
    """Test content hash computation."""

    def test_compute_content_hash_consistent(self, sample_repo_context):
        """Same inputs should produce the same hash."""
        repo_url = "https://github.com/user/repo"
        hash1 = TechniqueResultCache.compute_content_hash(repo_url, sample_repo_context)
        hash2 = TechniqueResultCache.compute_content_hash(repo_url, sample_repo_context)
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_compute_content_hash_changes_with_content(self, sample_repo_context):
        """Different content should produce different hashes."""
        repo_url = "https://github.com/user/repo"
        hash1 = TechniqueResultCache.compute_content_hash(repo_url, sample_repo_context)
        modified_context = sample_repo_context.copy()
        modified_context["readme"] = "Different readme content"
        hash2 = TechniqueResultCache.compute_content_hash(repo_url, modified_context)
        assert hash1 != hash2

    def test_compute_content_hash_different_repos(self, sample_repo_context):
        """Different repo URLs should produce different hashes."""
        hash1 = TechniqueResultCache.compute_content_hash(
            "https://github.com/user/repo1", sample_repo_context
        )
        hash2 = TechniqueResultCache.compute_content_hash(
            "https://github.com/user/repo2", sample_repo_context
        )
        assert hash1 != hash2


class TestCacheClear:
    """Test cache clear operation."""

    def test_clear_empties_cache(self, cache, sample_result):
        """Clear should remove all entries and reset stats."""
        cache.set("tech_1", "https://github.com/user/repo", "hash1", sample_result)
        cache.set("tech_2", "https://github.com/user/repo2", "hash2", sample_result)
        cache.get("tech_1", "https://github.com/user/repo", "hash1")
        cache.clear()
        assert len(cache._cache) == 0
        stats = cache.stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_entries == 0


class TestSingleton:
    """Test module-level singleton behavior."""

    def test_get_technique_cache_returns_same_instance(self):
        """get_technique_cache should return the same instance."""
        from app.techniques.cache import _cache_instance

        if _cache_instance is not None:
            _cache_instance.clear()
        cache1 = get_technique_cache()
        cache2 = get_technique_cache()
        assert cache1 is cache2

    def test_get_technique_cache_uses_settings_ttl(self):
        """get_technique_cache should use settings TTL."""
        from app.techniques.cache import _cache_instance

        if _cache_instance is not None:
            _cache_instance.clear()
        cache = get_technique_cache()
        assert cache._ttl == timedelta(hours=24)
