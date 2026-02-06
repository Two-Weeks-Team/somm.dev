"""Grand Tasting evaluation pipeline with 8 Tasting Notes nodes.

Architecture:
  START → RAG Enrich (optional)
                │
    ┌───────────┼───────────┐
    │     │     │     │     │
    ▼     ▼     ▼     ▼     ▼
  Aroma Palate Body Finish Balance
    │     │     │     │     │
    │     ▼     ▼     │     │
    │  Vintage Terroir │     │
    │     │     │     │     │
    └─────┴─────┴─────┴─────┘
                │
            Cellar (Synthesis) → END
"""

from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.graph.state import EvaluationState
from app.graph.checkpoint import get_checkpointer
from app.graph.nodes.tasting_notes import (
    AromaNotesNode,
    PalateNotesNode,
    BodyNotesNode,
    FinishNotesNode,
    BalanceNotesNode,
    VintageNotesNode,
    TerroirNotesNode,
    CellarNotesNode,
)
from app.graph.nodes.rag_enrich import rag_enrich


def create_grand_tasting_graph():
    aroma = AromaNotesNode()
    palate = PalateNotesNode()
    body = BodyNotesNode()
    finish = FinishNotesNode()
    balance = BalanceNotesNode()
    vintage = VintageNotesNode()
    terroir = TerroirNotesNode()
    cellar = CellarNotesNode()

    builder = StateGraph(EvaluationState)

    parallel_nodes = [
        "aroma",
        "palate",
        "body",
        "finish",
        "balance",
        "vintage",
        "terroir",
    ]

    if settings.RAG_ENABLED:
        builder.add_node("rag_enrich", rag_enrich)

    builder.add_node("aroma", aroma.evaluate)
    builder.add_node("palate", palate.evaluate)
    builder.add_node("body", body.evaluate)
    builder.add_node("finish", finish.evaluate)
    builder.add_node("balance", balance.evaluate)
    builder.add_node("vintage", vintage.evaluate)
    builder.add_node("terroir", terroir.evaluate)
    builder.add_node("cellar", cellar.evaluate)

    if settings.RAG_ENABLED:
        builder.add_edge("__start__", "rag_enrich")
        for node in parallel_nodes:
            builder.add_edge("rag_enrich", node)
    else:
        for node in parallel_nodes:
            builder.add_edge("__start__", node)

    for node in parallel_nodes:
        builder.add_edge(node, "cellar")

    builder.add_edge("cellar", END)

    checkpointer = get_checkpointer()
    return builder.compile(checkpointer=checkpointer)


_grand_tasting_graph = None


def get_grand_tasting_graph():
    global _grand_tasting_graph
    if _grand_tasting_graph is None:
        _grand_tasting_graph = create_grand_tasting_graph()
    return _grand_tasting_graph
