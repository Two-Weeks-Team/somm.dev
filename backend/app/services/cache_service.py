"""Cache service for graph visualization data."""

from app.database.repositories.graph_cache import GraphCacheRepository


def generate_cache_key(
    evaluation_id: str,
    mode: str,
    graph_type: str,
    schema_version: int = 2,
) -> str:
    return f"{evaluation_id}:{mode}:{graph_type}:v{schema_version}"


def get_graph_cache_repository() -> GraphCacheRepository:
    return GraphCacheRepository()
