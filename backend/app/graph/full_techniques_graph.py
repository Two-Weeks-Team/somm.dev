from langgraph.graph import StateGraph, END

__all__ = ["create_full_techniques_graph"]
from app.core.config import settings
from app.graph.state import EvaluationState
from app.graph.checkpoint import get_checkpointer
from app.graph.nodes.technique_categories import (
    AromaCategoryNode,
    PalateCategoryNode,
    BodyCategoryNode,
    FinishCategoryNode,
    BalanceCategoryNode,
    VintageCategoryNode,
    TerroirCategoryNode,
    CellarCategoryNode,
)
from app.graph.nodes.technique_categories.deep_synthesis import deep_synthesis
from app.graph.nodes.technique_categories.finalize import finalize
from app.graph.nodes.rag_enrich import rag_enrich
from app.graph.nodes.web_search_enrich import web_search_enrich
from app.graph.nodes.code_analysis_enrich import code_analysis_enrich


def create_full_techniques_graph():
    aroma = AromaCategoryNode()
    palate = PalateCategoryNode()
    body = BodyCategoryNode()
    finish = FinishCategoryNode()
    balance = BalanceCategoryNode()
    vintage = VintageCategoryNode()
    terroir = TerroirCategoryNode()
    cellar = CellarCategoryNode()

    builder = StateGraph(EvaluationState)

    category_nodes = [
        "aroma",
        "palate",
        "body",
        "finish",
        "balance",
        "vintage",
        "terroir",
        "cellar",
    ]

    enrichment_nodes = []

    if settings.RAG_ENABLED:
        builder.add_node("rag_enrich", rag_enrich)
        enrichment_nodes.append("rag_enrich")

    builder.add_node("web_search_enrich", web_search_enrich)
    enrichment_nodes.append("web_search_enrich")

    builder.add_node("code_analysis_enrich", code_analysis_enrich)
    enrichment_nodes.append("code_analysis_enrich")

    builder.add_node("aroma", aroma.evaluate)
    builder.add_node("palate", palate.evaluate)
    builder.add_node("body", body.evaluate)
    builder.add_node("finish", finish.evaluate)
    builder.add_node("balance", balance.evaluate)
    builder.add_node("vintage", vintage.evaluate)
    builder.add_node("terroir", terroir.evaluate)
    builder.add_node("cellar", cellar.evaluate)

    builder.add_node("deep_synthesis", deep_synthesis)
    builder.add_node("finalize", finalize)

    for enrich_node in enrichment_nodes:
        builder.add_edge("__start__", enrich_node)
        for node in category_nodes:
            builder.add_edge(enrich_node, node)

    for node in category_nodes:
        builder.add_edge(node, "deep_synthesis")

    builder.add_edge("deep_synthesis", "finalize")
    builder.add_edge("finalize", END)

    checkpointer = get_checkpointer()
    return builder.compile(checkpointer=checkpointer)
