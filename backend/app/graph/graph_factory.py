"""Graph Factory for selecting evaluation mode graphs.

This module provides graph builder registry and lookup functionality.
EvaluationMode enum is defined in app.models.graph to avoid circular imports.
"""

from typing import Callable, Dict

from langgraph.graph.state import CompiledStateGraph

# Re-export EvaluationMode from models for backward compatibility
from app.models.graph import EvaluationMode

__all__ = [
    "EvaluationMode",
    "InvalidEvaluationModeError",
    "get_evaluation_graph",
    "list_available_modes",
    "is_valid_mode",
]


class InvalidEvaluationModeError(Exception):
    def __init__(self, mode: str, available: list[str]):
        self.mode = mode
        self.available = available
        super().__init__(
            f"Invalid evaluation mode: '{mode}'. "
            f"Available modes: {', '.join(available)}"
        )


_graph_builders: Dict[str, Callable[[], CompiledStateGraph]] = {}


def _register_graphs():
    global _graph_builders
    if _graph_builders:
        return

    from app.graph.graph import create_evaluation_graph
    from app.graph.grand_tasting_graph import create_grand_tasting_graph
    from app.graph.full_techniques_graph import create_full_techniques_graph

    _graph_builders = {
        EvaluationMode.SIX_SOMMELIERS.value: create_evaluation_graph,
        EvaluationMode.GRAND_TASTING.value: create_grand_tasting_graph,
        EvaluationMode.FULL_TECHNIQUES.value: create_full_techniques_graph,
    }


def get_evaluation_graph(mode: str = "six_sommeliers") -> CompiledStateGraph:
    _register_graphs()

    if mode not in _graph_builders:
        raise InvalidEvaluationModeError(mode, list(_graph_builders.keys()))

    return _graph_builders[mode]()


def list_available_modes() -> list[str]:
    _register_graphs()
    return list(_graph_builders.keys())


def is_valid_mode(mode: str) -> bool:
    _register_graphs()
    return mode in _graph_builders
