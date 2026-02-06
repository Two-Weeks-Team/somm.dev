"""Graph cache repository for caching graph visualization payloads."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database.connection import get_database

logger = logging.getLogger(__name__)

COLLECTION_NAME = "graph_data"
DEFAULT_TTL_HOURS = 24


class GraphCacheRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            db = get_database()
            self._collection = db[COLLECTION_NAME]
        return self._collection

    async def get(self, cache_key: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"cache_key": cache_key})
            if doc is None:
                return None

            expires_at = doc.get("expires_at")
            if expires_at and datetime.now(timezone.utc) > expires_at.replace(
                tzinfo=timezone.utc
            ):
                return None

            return doc
        except Exception as e:
            logger.warning("Cache get failed for key %s: %s", cache_key, e)
            return None

    async def set(
        self,
        cache_key: str,
        graph_type: str,
        payload: dict,
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> str:
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=ttl_hours)

            document = {
                "cache_key": cache_key,
                "graph_type": graph_type,
                "payload": payload,
                "created_at": now,
                "expires_at": expires_at,
            }

            await self.collection.replace_one(
                {"cache_key": cache_key},
                document,
                upsert=True,
            )

            return cache_key
        except Exception as e:
            logger.warning("Cache set failed for key %s: %s", cache_key, e)
            return cache_key

    async def delete(self, cache_key: str) -> bool:
        try:
            result = await self.collection.delete_one({"cache_key": cache_key})
            return result.deleted_count > 0
        except Exception as e:
            logger.warning("Cache delete failed for key %s: %s", cache_key, e)
            return False

    async def exists(self, cache_key: str) -> bool:
        try:
            doc = await self.collection.find_one({"cache_key": cache_key})
            if doc is None:
                return False

            expires_at = doc.get("expires_at")
            if expires_at and datetime.now(timezone.utc) > expires_at.replace(
                tzinfo=timezone.utc
            ):
                return False

            return True
        except Exception as e:
            logger.warning("Cache exists check failed for key %s: %s", cache_key, e)
            return False

    async def clear_all(self) -> int:
        result = await self.collection.delete_many({})
        return result.deleted_count


async def create_indexes():
    db = get_database()
    await db[COLLECTION_NAME].create_index(
        "expires_at",
        expireAfterSeconds=0,
        name="ttl_expires_at",
    )
    await db[COLLECTION_NAME].create_index(
        "cache_key",
        unique=True,
        name="idx_cache_key",
    )
