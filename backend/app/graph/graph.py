"""LangGraph evaluation pipeline orchestration.

This module creates the evaluation graph that wires together all 6 sommelier nodes
with fan-out parallel execution from __start__ and fan-in to Jean-Pierre for synthesis.
"""

from langgraph.graph import StateGraph, END
from app.graph.state import EvaluationState
from app.graph.checkpoint import get_checkpointer
from app.graph.nodes.marcel import MarcelNode
from app.graph.nodes.isabella import IsabellaNode
from app.graph.nodes.heinrich import HeinrichNode
from app.graph.nodes.sofia import SofiaNode
from app.graph.nodes.laurent import LaurentNode
from app.graph.nodes.jeanpierre import JeanPierreNode


def create_evaluation_graph():
    """Create and configure the evaluation graph.

    The graph follows a fan-out/fan-in pattern:
    - Fan-out: 5 sommelier nodes run in parallel from __start__
    - Fan-in: All must complete before Jean-Pierre synthesis
    - End: Jean-Pierre connects to END after synthesis

    Returns:
        Compiled LangGraph with MongoDB checkpointer for state persistence.
    """
    marcel = MarcelNode()
    isabella = IsabellaNode()
    heinrich = HeinrichNode()
    sofia = SofiaNode()
    laurent = LaurentNode()
    jeanpierre = JeanPierreNode()

    builder = StateGraph(EvaluationState)

    # Add all sommelier nodes
    builder.add_node("marcel", marcel.evaluate)
    builder.add_node("isabella", isabella.evaluate)
    builder.add_node("heinrich", heinrich.evaluate)
    builder.add_node("sofia", sofia.evaluate)
    builder.add_node("laurent", laurent.evaluate)
    builder.add_node("jeanpierre", jeanpierre.evaluate)

    # Fan-out: Parallel execution from start
    builder.add_edge("__start__", "marcel")
    builder.add_edge("__start__", "isabella")
    builder.add_edge("__start__", "heinrich")
    builder.add_edge("__start__", "sofia")
    builder.add_edge("__start__", "laurent")

    # Fan-in: All must complete before Jean-Pierre
    builder.add_edge("marcel", "jeanpierre")
    builder.add_edge("isabella", "jeanpierre")
    builder.add_edge("heinrich", "jeanpierre")
    builder.add_edge("sofia", "jeanpierre")
    builder.add_edge("laurent", "jeanpierre")

    # End after synthesis
    builder.add_edge("jeanpierre", END)

    checkpointer = get_checkpointer()
    return builder.compile(checkpointer=checkpointer)


# Lazy-loaded evaluation graph (created on first access)
_evaluation_graph = None


def get_evaluation_graph():
    """Get or create the evaluation graph.

    This function implements lazy initialization to avoid database
    connection requirements at module import time.

    Returns:
        Compiled LangGraph with MongoDB checkpointer for state persistence.
    """
    global _evaluation_graph
    if _evaluation_graph is None:
        _evaluation_graph = create_evaluation_graph()
    return _evaluation_graph


# Module-level lazy-loaded evaluation graph
# Accessing this triggers graph creation if not already created
def __getattr__(name):
    """Module-level lazy loading for evaluation_graph."""
    if name == "evaluation_graph":
        return get_evaluation_graph()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
