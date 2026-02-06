"""Graph package for LangGraph evaluation pipeline.

This module exports the compiled evaluation graph for LangGraph Server discovery.
The graph can be accessed via:
- Direct import: `from app.graph import evaluation_graph`
- LangGraph Server: Configure in langgraph.json as "app.graph:evaluation_graph"
"""

from app.graph.graph import (
    create_evaluation_graph,
    get_evaluation_graph,
)
from app.graph.state import EvaluationState


# Module-level export for LangGraph Server discovery
# This lazy-loads the graph to avoid database connection at import time
def __getattr__(name: str):
    """Lazy load evaluation_graph for LangGraph Server compatibility."""
    if name == "evaluation_graph":
        return get_evaluation_graph()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "evaluation_graph",
    "create_evaluation_graph",
    "get_evaluation_graph",
    "EvaluationState",
]
