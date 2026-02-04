"""MongoDB checkpointer for LangGraph state persistence."""

from langgraph.checkpoint.mongodb import MongoDBSaver
from app.database.connection import get_database


def get_checkpointer():
    """Create and return a MongoDB checkpointer for LangGraph.

    Returns:
        MongoDBSaver: A checkpointer configured to persist graph state
                     in the MongoDB checkpoints collection.
    """
    db = get_database()
    return MongoDBSaver(db=db, collection_name="checkpoints")
