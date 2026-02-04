# Draft: LangChain/LangGraph Architecture Update

## Requirements Confirmed

The backend MUST comply with LangChain and LangGraph standard patterns:

1. **StateGraph with TypedDict** - Graph state management
2. **Conditional edges** - Dynamic routing based on state
3. **Parallel execution** - Fan-out/fan-in with `operator.add` reducers
4. **Send API** - Map-reduce pattern for sommelier distribution
5. **Checkpointing** - SqliteSaver/MemorySaver for persistence
6. **Streaming** - `astream` and `astream_events` for real-time updates
7. **Structured output** - Pydantic models with `with_structured_output`
8. **LCEL** - LangChain Expression Language for chains
9. **Async patterns** - Throughout all LLM calls
10. **Error handling** - Retry decorators, validation handlers

## Research Findings

### LangGraph StateGraph Pattern
```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
import operator

class EvaluationState(TypedDict):
    repo_url: str
    repo_context: dict
    sommelier_results: Annotated[list, operator.add]  # Reducer for parallel nodes
    final_score: int
    status: str
```

### Parallel Sommelier Execution (Fan-out/Fan-in)
```python
from langgraph.types import Send

def distribute_to_sommeliers(state: EvaluationState):
    """Fan-out: send to all 6 sommeliers in parallel"""
    return [
        Send("sommelier_marcel", state),
        Send("sommelier_isabella", state),
        Send("sommelier_heinrich", state),
        Send("sommelier_sofia", state),
        Send("sommelier_laurent", state),
        Send("sommelier_jeanpierre", state),
    ]
```

### Checkpointing for Persistence
```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("evaluations.db")
graph = builder.compile(checkpointer=checkpointer)

# Resume evaluation if interrupted
config = {"configurable": {"thread_id": f"eval-{job_id}"}}
result = graph.invoke(initial_state, config)
```

### Streaming Events
```python
async for event in graph.astream_events(
    initial_state,
    config,
    version="v2"
):
    if event["event"] == "on_chain_end":
        yield SSEEvent(
            type="sommelier_complete",
            sommelier=event["name"],
            data=event["data"]
        )
```

### Structured Output with Pydantic
```python
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

class SommelierOutput(BaseModel):
    notes: str = Field(description="Wine-themed evaluation notes")
    score: int = Field(description="Score 0-100", ge=0, le=100)
    confidence: float = Field(description="Confidence 0-1", ge=0, le=1)
    techniques_used: list[str] = Field(description="Techniques applied")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
structured_llm = llm.with_structured_output(SommelierOutput)
```

## Documents to Update/Create

### 1. docs/ARCHITECTURE.md
- Add LangGraph workflow diagram
- Show StateGraph structure
- Document fan-out/fan-in pattern for sommeliers

### 2. docs/EVALUATION_PIPELINE.md (MAJOR UPDATE)
- Complete LangGraph workflow specification
- StateGraph node definitions
- Edge routing logic
- Checkpointing strategy
- Streaming event emission

### 3. docs/SOMMELIER_AGENTS.md (UPDATE)
- LangChain ChatModel integration
- Structured output schemas (Pydantic)
- LCEL prompt chains
- Async patterns

### 4. docs/TECHNICAL_SPECIFICATION.md (NEW)
- Complete LangChain/LangGraph spec
- State management patterns
- Error handling strategies
- Retry configurations

### 5. docs/IMPLEMENTATION_GUIDE.md (NEW)
- Step-by-step LangGraph setup
- Code examples for each component
- Testing strategies

## Graph Structure

```
                    ┌─────────────────┐
                    │   START         │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  fetch_context  │
                    │  (GitHub API)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ select_techniques│
                    │  (Dynamic AI)   │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │  Marcel  │       │ Isabella │       │ Heinrich │
    │ (Cellar) │       │ (Critic) │       │(Inspector)│
    └────┬─────┘       └────┬─────┘       └────┬─────┘
          │                  │                  │
          │     ┌────────────┼────────────┐    │
          │     │            │            │    │
          ▼     ▼            ▼            ▼    ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐
       │  Sofia   │    │ Laurent  │    │(continues)│
       │ (Scout)  │    │(Winemaker)│    │          │
       └────┬─────┘    └────┬─────┘    └────┬─────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │  Jean-Pierre    │
                    │  (Synthesis)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      END        │
                    └─────────────────┘
```

## Open Questions

1. **Checkpointer choice**: SqliteSaver vs MongoDB-based custom checkpointer?
2. **Model provider**: Use `langchain-google-genai` for Gemini 3?
3. **Memory management**: Include conversation memory or stateless?
