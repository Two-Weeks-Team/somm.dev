"""Tests for GraphCacheRepository and cache_service."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database.repositories.graph_cache import (
    GraphCacheRepository,
    create_indexes,
    DEFAULT_TTL_HOURS,
)
from app.services.cache_service import (
    generate_cache_key,
    get_graph_cache_repository,
)


class TestCacheKeyGeneration:
    def test_generate_cache_key_basic(self):
        key = generate_cache_key("eval_abc123", "six_sommeliers", "2d")
        assert key == "eval_abc123:six_sommeliers:2d:v2"

    def test_generate_cache_key_3d(self):
        key = generate_cache_key("eval_xyz789", "basic", "3d")
        assert key == "eval_xyz789:basic:3d:v2"

    def test_generate_cache_key_custom_version(self):
        key = generate_cache_key(
            "eval_abc123", "six_sommeliers", "2d", schema_version=3
        )
        assert key == "eval_abc123:six_sommeliers:2d:v3"

    def test_generate_cache_key_stability(self):
        key1 = generate_cache_key("eval_abc", "mode1", "2d")
        key2 = generate_cache_key("eval_abc", "mode1", "2d")
        key3 = generate_cache_key("eval_abc", "mode1", "2d", schema_version=2)
        assert key1 == key2 == key3

    def test_generate_cache_key_different_inputs(self):
        key1 = generate_cache_key("eval_abc", "mode1", "2d")
        key2 = generate_cache_key("eval_abc", "mode1", "3d")
        key3 = generate_cache_key("eval_abc", "mode2", "2d")
        key4 = generate_cache_key("eval_xyz", "mode1", "2d")

        assert key1 != key2
        assert key1 != key3
        assert key1 != key4


class TestGraphCacheRepositoryUnit:
    @pytest.fixture
    def mock_collection(self):
        collection = AsyncMock()
        return collection

    @pytest.fixture
    def repo(self, mock_collection):
        repository = GraphCacheRepository()
        repository._collection = mock_collection
        return repository

    @pytest.mark.asyncio
    async def test_get_cache_hit(self, repo, mock_collection):
        now = datetime.now(timezone.utc)
        cached_doc = {
            "cache_key": "test:key:2d:v2",
            "graph_type": "2d",
            "payload": {"nodes": [], "edges": []},
            "created_at": now,
            "expires_at": now + timedelta(hours=24),
        }
        mock_collection.find_one.return_value = cached_doc

        result = await repo.get("test:key:2d:v2")

        assert result is not None
        assert result["cache_key"] == "test:key:2d:v2"
        mock_collection.find_one.assert_called_once_with(
            {"cache_key": "test:key:2d:v2"}
        )

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, repo, mock_collection):
        mock_collection.find_one.return_value = None

        result = await repo.get("test:nonexistent:2d:v2")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_expired_cache(self, repo, mock_collection):
        now = datetime.now(timezone.utc)
        expired_doc = {
            "cache_key": "test:expired:2d:v2",
            "graph_type": "2d",
            "payload": {"nodes": [], "edges": []},
            "created_at": now - timedelta(hours=48),
            "expires_at": now - timedelta(hours=24),
        }
        mock_collection.find_one.return_value = expired_doc

        result = await repo.get("test:expired:2d:v2")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_exception(self, repo, mock_collection):
        mock_collection.find_one.side_effect = Exception("DB error")

        result = await repo.get("test:key:2d:v2")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_creates_document(self, repo, mock_collection):
        payload = {"nodes": [{"id": "node1"}], "edges": []}

        result = await repo.set("test:key:2d:v2", "2d", payload)

        assert result == "test:key:2d:v2"
        mock_collection.replace_one.assert_called_once()
        call_args = mock_collection.replace_one.call_args
        assert call_args[0][0] == {"cache_key": "test:key:2d:v2"}
        assert call_args[1]["upsert"] is True

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, repo, mock_collection):
        payload = {"nodes": [], "edges": []}

        await repo.set("test:key:2d:v2", "2d", payload, ttl_hours=48)

        call_args = mock_collection.replace_one.call_args
        doc = call_args[0][1]
        assert "expires_at" in doc
        expected_expiry = datetime.now(timezone.utc) + timedelta(hours=48)
        assert abs((doc["expires_at"] - expected_expiry).total_seconds()) < 5

    @pytest.mark.asyncio
    async def test_delete_existing(self, repo, mock_collection):
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_delete_result

        result = await repo.delete("test:key:2d:v2")

        assert result is True
        mock_collection.delete_one.assert_called_once_with(
            {"cache_key": "test:key:2d:v2"}
        )

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, repo, mock_collection):
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 0
        mock_collection.delete_one.return_value = mock_delete_result

        result = await repo.delete("test:nonexistent:2d:v2")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self, repo, mock_collection):
        now = datetime.now(timezone.utc)
        mock_collection.find_one.return_value = {
            "cache_key": "test:key:2d:v2",
            "expires_at": now + timedelta(hours=24),
        }

        result = await repo.exists("test:key:2d:v2")

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false_not_found(self, repo, mock_collection):
        mock_collection.find_one.return_value = None

        result = await repo.exists("test:nonexistent:2d:v2")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_false_expired(self, repo, mock_collection):
        now = datetime.now(timezone.utc)
        mock_collection.find_one.return_value = {
            "cache_key": "test:expired:2d:v2",
            "expires_at": now - timedelta(hours=1),
        }

        result = await repo.exists("test:expired:2d:v2")

        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all(self, repo, mock_collection):
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 5
        mock_collection.delete_many.return_value = mock_delete_result

        result = await repo.clear_all()

        assert result == 5
        mock_collection.delete_many.assert_called_once_with({})


class TestCacheService:
    def test_get_graph_cache_repository(self):
        repo1 = get_graph_cache_repository()
        repo2 = get_graph_cache_repository()

        assert isinstance(repo1, GraphCacheRepository)
        assert isinstance(repo2, GraphCacheRepository)
        assert repo1 is not repo2

    def test_default_ttl_hours(self):
        assert DEFAULT_TTL_HOURS == 24


@pytest.mark.skip(reason="Requires MongoDB connection")
@pytest.mark.asyncio
class TestGraphCacheRepositoryIntegration:
    @pytest.fixture
    async def repo(self):
        repository = GraphCacheRepository()
        await repository.clear_all()
        yield repository
        await repository.clear_all()

    async def test_full_cache_lifecycle(self, repo):
        cache_key = "test:lifecycle:2d:v2"
        payload = {
            "nodes": [{"id": "node1", "position": {"x": 0, "y": 0}}],
            "edges": [],
        }

        assert await repo.exists(cache_key) is False
        assert await repo.get(cache_key) is None

        await repo.set(cache_key, "2d", payload)

        assert await repo.exists(cache_key) is True

        cached = await repo.get(cache_key)
        assert cached is not None
        assert cached["cache_key"] == cache_key
        assert cached["graph_type"] == "2d"
        assert cached["payload"] == payload

        deleted = await repo.delete(cache_key)
        assert deleted is True

        assert await repo.exists(cache_key) is False

    async def test_ttl_index_creation(self, repo):
        await create_indexes()

        indexes = await repo.collection.list_indexes().to_list(length=None)
        index_names = [idx["name"] for idx in indexes]

        assert "ttl_expires_at" in index_names

        ttl_index = next(
            (idx for idx in indexes if idx["name"] == "ttl_expires_at"), None
        )
        assert ttl_index is not None
        assert ttl_index.get("expireAfterSeconds") == 0
