"""MongoDB checkpointer for LangGraph state persistence."""

from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.core.config import settings

# Module-level sync client for checkpointer (MongoDBSaver requires pymongo, not motor)
_sync_client: MongoClient | None = None


def _get_sync_client() -> MongoClient:
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(settings.MONGODB_URI)
    return _sync_client


def get_checkpointer() -> MongoDBSaver:
    # MongoDBSaver requires sync pymongo.MongoClient, not async Motor
    client = _get_sync_client()
    return MongoDBSaver(
        client=client,
        db_name=settings.MONGO_DB,
        checkpoint_collection_name="checkpoints",
    )
