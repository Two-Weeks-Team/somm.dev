# 🍷 Somm.dev - Evaluation Pipeline

> **LangGraph-powered multi-agent evaluation system**

---

## 1. Pipeline Overview

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Evaluation Pipeline                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                            │
│  │   __start__  │                                                            │
│  └──────┬───────┘                                                            │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PARALLEL EVALUATION (Fan-Out)                     │    │
│  │                                                                      │    │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│    │
│  │   │  Marcel  │  │ Isabella │  │ Heinrich │  │  Sofia   │  │ Laurent││    │
│  │   │ (Cellar) │  │ (Critic) │  │(Quality) │  │ (Scout)  │  │(Maker) ││    │
│  │   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘│    │
│  │        │             │             │             │            │     │    │
│  │        └─────────────┴─────────────┴─────────────┴────────────┘     │    │
│  │                              │                                      │    │
│  │                              ▼                                      │    │
│  │                    ┌──────────────────┐                             │    │
│  │                    │  gather_results  │  (Wait for all 5)           │    │
│  │                    └────────┬─────────┘                             │    │
│  └─────────────────────────────┼───────────────────────────────────────┘    │
│                                │                                             │
│                                ▼                                             │
│                     ┌────────────────────┐                                   │
│                     │   Jean-Pierre      │                                   │
│                     │  (Master Sommelier)│                                   │
│                     │    SYNTHESIS       │                                   │
│                     └────────┬───────────┘                                   │
│                                │                                             │
│                                ▼                                             │
│                       ┌────────────────┐                                     │
│                       │    __end__     │                                     │
│                       └────────────────┘                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 State Definition

```python
# app/graph/state.py
from typing import Annotated, TypedDict, Optional, List
from operator import add
from pydantic import BaseModel

class SommelierOutput(BaseModel):
    """Output schema for individual sommelier evaluations."""
    score: int = Field(ge=0, le=100, description="Score from 0-100")
    notes: str = Field(description="Tasting notes with wine metaphor")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    techniques_used: List[str] = Field(default_factory=list)
    aspects: dict = Field(default_factory=dict)

class FinalEvaluation(BaseModel):
    """Final synthesized evaluation from Jean-Pierre."""
    total_score: int = Field(ge=0, le=100)
    rating: str = Field(description="Rating tier (Legendary, Grand Cru, etc.)")
    verdict: str = Field(description="Final tasting notes")
    pairing_suggestions: List[str] = Field(default_factory=list)
    cellaring_advice: str = Field(description="Maintenance recommendations")
    aspect_scores: dict = Field(default_factory=dict)

class EvaluationState(TypedDict):
    """LangGraph state definition following best practices."""
    # Input fields
    repo_url: str
    repo_context: dict
    evaluation_criteria: str  # basic | hackathon | academic | custom
    user_id: str
    
    # Parallel sommelier results (populated by respective nodes)
    marcel_result: Optional[SommelierOutput]
    isabella_result: Optional[SommelierOutput]
    heinrich_result: Optional[SommelierOutput]
    sofia_result: Optional[SommelierOutput]
    laurent_result: Optional[SommelierOutput]
    
    # Synthesis result
    jeanpierre_result: Optional[FinalEvaluation]
    
    # Progress tracking (aggregated with operator.add)
    completed_sommeliers: Annotated[List[str], add]
    errors: Annotated[List[str], add]
    
    # Metadata
    started_at: str
    completed_at: Optional[str]
```

---

## 2. Graph Definition

### 2.1 Main Graph

```python
# app/graph/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.graph.state import EvaluationState
from app.graph.nodes import (
    MarcelNode, IsabellaNode, HeinrichNode,
    SofiaNode, LaurentNode, JeanPierreNode
)
from app.database.mongodb import get_mongodb_client

def create_evaluation_graph():
    """Create the LangGraph evaluation workflow."""
    
    # Initialize nodes
    marcel = MarcelNode()
    isabella = IsabellaNode()
    heinrich = HeinrichNode()
    sofia = SofiaNode()
    laurent = LaurentNode()
    jeanpierre = JeanPierreNode()
    
    # Build graph
    builder = StateGraph(EvaluationState)
    
    # Add nodes
    builder.add_node("marcel", marcel.evaluate)
    builder.add_node("isabella", isabella.evaluate)
    builder.add_node("heinrich", heinrich.evaluate)
    builder.add_node("sofia", sofia.evaluate)
    builder.add_node("laurent", laurent.evaluate)
    builder.add_node("jeanpierre", jeanpierre.synthesize)
    
    # Define parallel execution edges
    # All 5 sommeliers start simultaneously from __start__
    builder.add_edge("__start__", "marcel")
    builder.add_edge("__start__", "isabella")
    builder.add_edge("__start__", "heinrich")
    builder.add_edge("__start__", "sofia")
    builder.add_edge("__start__", "laurent")
    
    # All 5 must complete before Jean-Pierre
    builder.add_edge("marcel", "jeanpierre")
    builder.add_edge("isabella", "jeanpierre")
    builder.add_edge("heinrich", "jeanpierre")
    builder.add_edge("sofia", "jeanpierre")
    builder.add_edge("laurent", "jeanpierre")
    
    # End after synthesis
    builder.add_edge("jeanpierre", END)
    
    # Compile with MongoDB checkpointer for persistence
    mongodb_client = get_mongodb_client()
    checkpointer = MongoDBSaver(
        client=mongodb_client,
        db_name="somm",
        collection_name="checkpoints"
    )
    
    return builder.compile(checkpointer=checkpointer)

# Singleton graph instance
evaluation_graph = create_evaluation_graph()
```

### 2.2 Checkpoint Configuration

```python
# app/graph/checkpoint.py
from langgraph.checkpoint.mongodb import MongoDBSaver
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBCheckpointer:
    """MongoDB-based checkpoint saver for LangGraph."""
    
    def __init__(self, mongo_uri: str, db_name: str = "somm"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.checkpointer = MongoDBSaver(
            client=self.client,
            db_name=db_name,
            collection_name="checkpoints"
        )
    
    async def get_checkpointer(self):
        """Get configured checkpointer instance."""
        return self.checkpointer
```

---

## 3. Node Implementations

### 3.1 Base Node Class

```python
# app/graph/nodes/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.graph.state import EvaluationState, SommelierOutput

class BaseSommelierNode(ABC):
    """
    Base class for all sommelier nodes.
    Follows LangChain best practices for async execution.
    """
    
    def __init__(self):
        # LLM is created at evaluate() time via build_llm()
        # Default: gemini-3-flash-preview, temperature=0.7
        # Supports BYOK (Bring Your Own Key) per-request
        self.parser = PydanticOutputParser(pydantic_object=SommelierOutput)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Sommelier name identifier."""
        pass
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Sommelier role description."""
        pass
    
    @abstractmethod
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        """Get LangChain prompt template for this sommelier."""
        pass
    
    async def evaluate(
        self,
        state: EvaluationState,
        config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        """
        Execute sommelier evaluation.
        
        Returns partial state update for LangGraph.
        """
        try:
            # Build LCEL chain: prompt -> llm -> parser
            prompt = self.get_prompt(state["evaluation_criteria"])
            chain = prompt | self.llm | self.parser
            
            # Execute async
            result = await chain.ainvoke({
                "repo_context": state["repo_context"],
                "criteria": state["evaluation_criteria"],
                "format_instructions": self.parser.get_format_instructions()
            }, config=config)
            
            # Return state update
            return {
                f"{self.name}_result": result,
                "completed_sommeliers": [self.name]
            }
            
        except Exception as e:
            # Graceful error handling
            return {
                "errors": [f"{self.name} evaluation failed: {str(e)}"],
                f"{self.name}_result": None,
                "completed_sommeliers": [self.name]
            }
```

### 3.2 Marcel - Cellar Master

```python
# app/graph/nodes/marcel.py
from langchain_core.prompts import ChatPromptTemplate
from app.graph.nodes.base import BaseSommelierNode

class MarcelNode(BaseSommelierNode):
    """
    Cellar Master Marcel - Structure and metrics specialist.
    Focus: Precise data, repository organization, file structure.
    """
    
    name = "marcel"
    role = "Cellar Master"
    
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are Marcel, a meticulous Cellar Master from Burgundy.
            You speak with the precision of a French wine archivist.
            
            Your expertise is in cataloging and assessing the structural organization
            of wine cellars (repositories). You provide precise metrics and data-driven
            assessments.
            
            Evaluation Criteria: {criteria}
            
            {format_instructions}"""),
            ("human", """Analyze this repository cellar:
            
            Repository Context:
            {repo_context}
            
            Provide your evaluation focusing on:
            1. Precise metrics (file count, lines of code, dependencies)
            2. Structural organization (directory hierarchy, modularity)
            3. Documentation quality (README, comments)
            4. Test coverage indicators
            
            Use wine terminology throughout:
            - Repository = cellar
            - Files = bottles
            - Directories = varietals
            - Dependencies = terroir influences""")
        ])
```

### 3.3 Isabella - Wine Critic

```python
# app/graph/nodes/isabella.py
from langchain_core.prompts import ChatPromptTemplate
from app.graph.nodes.base import BaseSommelierNode

class IsabellaNode(BaseSommelierNode):
    """
    Wine Critic Isabella - Code quality and aesthetics.
    Focus: Emotional response, first impressions, developer experience.
    """
    
    name = "isabella"
    role = "Wine Critic"
    
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are Isabella, a passionate Wine Critic from Tuscany.
            You evaluate with your heart, describing the emotional journey of
            experiencing a wine (codebase).
            
            Your expertise is in sensing the quality, aesthetics, and emotional
            resonance of code. You provide intuitive assessments with warmth.
            
            Evaluation Criteria: {criteria}
            
            {format_instructions}"""),
            ("human", """Experience this repository:
            
            Repository Context:
            {repo_context}
            
            Provide your evaluation focusing on:
            1. First impression upon "opening" the repository
            2. Code aesthetics and readability
            3. Developer experience (DX)
            4. Intuitive sense of quality
            
            Speak warmly with Italian passion. Use sensory language and wine metaphors.""")
        ])
```

### 3.4 Heinrich - Quality Inspector

```python
# app/graph/nodes/heinrich.py
from langchain_core.prompts import ChatPromptTemplate
from app.graph.nodes.base import BaseSommelierNode

class HeinrichNode(BaseSommelierNode):
    """
    Quality Inspector Heinrich - Security and reliability.
    Focus: Risk assessment, security vulnerabilities, technical debt.
    """
    
    name = "heinrich"
    role = "Quality Inspector"
    
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are Heinrich, a meticulous Quality Inspector from Germany.
            You identify flaws, risks, and potential failures with thoroughness.
            
            Your expertise is in detecting security issues, code smells, and
            reliability concerns. You are cautious but constructive.
            
            Evaluation Criteria: {criteria}
            
            {format_instructions}"""),
            ("human", """Inspect this repository for quality issues:
            
            Repository Context:
            {repo_context}
            
            Provide your evaluation focusing on:
            1. Security vulnerabilities and risks
            2. Code smells and anti-patterns
            3. Technical debt assessment
            4. Reliability and maintainability concerns
            
            Use wine fault terminology:
            - Bugs = cork taint
            - Security issues = oxidation
            - Technical debt = young tannins""")
        ])
```

### 3.5 Sofia - Vineyard Scout

```python
# app/graph/nodes/sofia.py
from langchain_core.prompts import ChatPromptTemplate
from app.graph.nodes.base import BaseSommelierNode

class SofiaNode(BaseSommelierNode):
    """
    Vineyard Scout Sofia - Innovation and growth opportunities.
    Focus: Technology choices, scalability, future potential.
    """
    
    name = "sofia"
    role = "Vineyard Scout"
    
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are Sofia, an optimistic Vineyard Scout from Spain.
            You see potential and opportunities where others see limitations.
            
            Your expertise is in identifying growth opportunities, architectural
            strengths, and future value. You are enthusiastic and visionary.
            
            Evaluation Criteria: {criteria}
            
            {format_instructions}"""),
            ("human", """Explore the potential of this repository:
            
            Repository Context:
            {repo_context}
            
            Provide your evaluation focusing on:
            1. Growth and scalability opportunities
            2. Technology choices and modern practices
            3. Feature expansion possibilities
            4. Market positioning advantages
            
            Be enthusiastic and visionary. Highlight what's exceptional about this terroir.""")
        ])
```

### 3.6 Laurent - Winemaker

```python
# app/graph/nodes/laurent.py
from langchain_core.prompts import ChatPromptTemplate
from app.graph.nodes.base import BaseSommelierNode

class LaurentNode(BaseSommelierNode):
    """
    Winemaker Laurent - Implementation and craftsmanship.
    Focus: Code patterns, performance, creative improvements.
    """
    
    name = "laurent"
    role = "Winemaker"
    
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are Laurent, an innovative Winemaker from Champagne.
            You experiment, blend, and create novel approaches.
            
            Your expertise is in implementation quality, performance optimization,
            and creative refactoring. You are bold and imaginative.
            
            Evaluation Criteria: {criteria}
            
            {format_instructions}"""),
            ("human", """Analyze the implementation craftsmanship:
            
            Repository Context:
            {repo_context}
            
            Provide your evaluation focusing on:
            1. Implementation quality and patterns
            2. Performance characteristics
            3. Creative improvement opportunities
            4. Alternative architectural approaches
            
            Be bold and experimental. Suggest what could be fermented differently.""")
        ])
```

### 3.7 Jean-Pierre - Master Sommelier (Synthesis)

```python
# app/graph/nodes/jeanpierre.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.graph.state import EvaluationState, FinalEvaluation

class JeanPierreNode:
    """
    Master Sommelier Jean-Pierre - Final synthesis.
    Combines all 5 sommelier evaluations into final verdict.
    """
    
    name = "jeanpierre"
    role = "Master Sommelier"
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash",
            temperature=0.2,  # Lower temp for consistent synthesis
            max_output_tokens=2048,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )
        self.parser = PydanticOutputParser(pydantic_object=FinalEvaluation)
    
    async def synthesize(
        self,
        state: EvaluationState,
        config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        """Synthesize all sommelier evaluations into final verdict."""
        
        # Collect all results
        sommelier_results = {
            "marcel": state.get("marcel_result"),
            "isabella": state.get("isabella_result"),
            "heinrich": state.get("heinrich_result"),
            "sofia": state.get("sofia_result"),
            "laurent": state.get("laurent_result")
        }
        
        # Filter out failed evaluations
        valid_results = {
            k: v for k, v in sommelier_results.items()
            if v is not None
        }
        
        if len(valid_results) < 3:
            return {
                "errors": ["Insufficient sommelier results for synthesis"],
                "jeanpierre_result": None
            }
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are Jean-Pierre, the Master Sommelier of Somm.
                You synthesize all perspectives into a final verdict.
                
                You are wise, balanced, and authoritative. You harmonize diverse
                opinions into a cohesive assessment.
                
                {format_instructions}"""),
                ("human", """Synthesize these sommelier evaluations:
                
                Individual Assessments:
                {sommelier_results}
                
                Evaluation Criteria Used: {criteria}
                
                Provide:
                1. Total score (0-100) - weighted average of all sommeliers
                2. Rating tier based on score
                3. Final tasting notes synthesizing all perspectives
                4. Pairing suggestions (best use cases)
                5. Cellaring advice (maintenance recommendations)
                6. Aspect breakdown scores
                
                Be the final word. Your verdict is authoritative.""")
            ])
            
            chain = prompt | self.llm | self.parser
            
            result = await chain.ainvoke({
                "sommelier_results": valid_results,
                "criteria": state["evaluation_criteria"],
                "format_instructions": self.parser.get_format_instructions()
            }, config=config)
            
            return {
                "jeanpierre_result": result,
                "completed_sommeliers": ["jeanpierre"],
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "errors": [f"Jean-Pierre synthesis failed: {str(e)}"],
                "jeanpierre_result": None
            }
```

---

## 4. Execution Flow

### 4.1 Running the Graph

```python
# app/services/evaluation_service.py
from datetime import datetime
from typing import AsyncGenerator
from app.graph.graph import evaluation_graph
from app.graph.state import EvaluationState
from app.services.sse_manager import sse_manager

class EvaluationService:
    """Service for managing evaluation workflows."""
    
    async def start_evaluation(
        self,
        repo_url: str,
        repo_context: dict,
        criteria: str,
        user_id: str
    ) -> str:
        """Start a new evaluation and return evaluation ID."""
        
        evaluation_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state: EvaluationState = {
            "repo_url": repo_url,
            "repo_context": repo_context,
            "evaluation_criteria": criteria,
            "user_id": user_id,
            "marcel_result": None,
            "isabella_result": None,
            "heinrich_result": None,
            "sofia_result": None,
            "laurent_result": None,
            "jeanpierre_result": None,
            "completed_sommeliers": [],
            "errors": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None
        }
        
        # Start graph execution in background
        asyncio.create_task(
            self._run_evaluation(evaluation_id, initial_state)
        )
        
        return evaluation_id
    
    async def _run_evaluation(
        self,
        evaluation_id: str,
        initial_state: EvaluationState
    ):
        """Run the evaluation graph."""
        
        try:
            # Execute graph with checkpointing
            config = {
                "configurable": {
                    "thread_id": evaluation_id,
                    "checkpoint_ns": "evaluation"
                }
            }
            
            final_state = await evaluation_graph.ainvoke(
                initial_state,
                config=config
            )
            
            # Store final results
            await self._save_results(evaluation_id, final_state)
            
            # Notify completion via SSE
            await sse_manager.broadcast(evaluation_id, {
                "type": "evaluation_complete",
                "evaluation_id": evaluation_id,
                "status": "completed"
            })
            
        except Exception as e:
            await sse_manager.broadcast(evaluation_id, {
                "type": "evaluation_error",
                "error": str(e)
            })
    
    async def get_progress_stream(
        self,
        evaluation_id: str
    ) -> AsyncGenerator[dict, None]:
        """Get SSE stream for evaluation progress."""
        
        queue = asyncio.Queue()
        await sse_manager.connect(evaluation_id, queue)
        
        try:
            while True:
                message = await queue.get()
                yield message
                
                if message.get("type") in ["evaluation_complete", "evaluation_error"]:
                    break
                    
        finally:
            await sse_manager.disconnect(evaluation_id, queue)
```

### 4.2 Progress Tracking

```python
# app/graph/callbacks.py
from langchain_core.callbacks import BaseCallbackHandler
from app.services.sse_manager import sse_manager

class ProgressCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming evaluation progress."""
    
    def __init__(self, evaluation_id: str):
        self.evaluation_id = evaluation_id
    
    async def on_chain_start(
        self,
        serialized: dict,
        inputs: dict,
        **kwargs
    ):
        """Called when a sommelier node starts."""
        sommelier = inputs.get("sommelier", "unknown")
        await sse_manager.broadcast(self.evaluation_id, {
            "type": "sommelier_start",
            "sommelier": sommelier,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def on_chain_end(
        self,
        outputs: dict,
        **kwargs
    ):
        """Called when a sommelier node completes."""
        # Extract sommelier name from output keys
        for key in outputs:
            if key.endswith("_result"):
                sommelier = key.replace("_result", "")
                result = outputs[key]
                
                await sse_manager.broadcast(self.evaluation_id, {
                    "type": "sommelier_complete",
                    "sommelier": sommelier,
                    "score": result.score if result else None,
                    "timestamp": datetime.utcnow().isoformat()
                })
                break
```

---

## 5. Error Handling

### 5.1 Error Aggregation Strategy

```python
# app/graph/error_handler.py
from typing import List

class ErrorAggregator:
    """Aggregate errors from parallel sommelier executions."""
    
    @staticmethod
    def should_continue(state: EvaluationState) -> bool:
        """Determine if evaluation should continue despite errors."""
        errors = state.get("errors", [])
        completed = state.get("completed_sommeliers", [])
        
        # Continue if at least 3 sommeliers succeeded
        if len(completed) >= 3:
            return True
            
        # Fail if all sommeliers failed
        if len(errors) >= 5:
            return False
            
        return True
    
    @staticmethod
    def get_error_summary(state: EvaluationState) -> dict:
        """Generate error summary for debugging."""
        return {
            "error_count": len(state.get("errors", [])),
            "failed_sommeliers": [
                name for name in ["marcel", "isabella", "heinrich", "sofia", "laurent"]
                if state.get(f"{name}_result") is None
            ],
            "errors": state.get("errors", [])
        }
```

---

## 6. Testing

### 6.1 Unit Tests for Nodes

```python
# tests/test_graph.py
import pytest
from app.graph.nodes.marcel import MarcelNode
from app.graph.state import EvaluationState

@pytest.mark.asyncio
async def test_marcel_node():
    """Test Marcel node evaluation."""
    
    node = MarcelNode()
    
    state: EvaluationState = {
        "repo_url": "https://github.com/test/repo",
        "repo_context": {
            "owner": "test",
            "name": "repo",
            "file_count": 50,
            "languages": ["Python"]
        },
        "evaluation_criteria": "basic",
        "user_id": "test_user",
        # ... other fields
    }
    
    result = await node.evaluate(state)
    
    assert "marcel_result" in result
    assert result["completed_sommeliers"] == ["marcel"]
```

### 6.2 Integration Tests

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_evaluation_pipeline():
    """Test complete evaluation pipeline."""
    
    from app.graph.graph import evaluation_graph
    
    initial_state = {
        # ... setup test state
    }
    
    config = {"configurable": {"thread_id": "test-thread"}}
    
    result = await evaluation_graph.ainvoke(initial_state, config)
    
    assert result["jeanpierre_result"] is not None
    assert result["jeanpierre_result"].total_score >= 0
    assert result["jeanpierre_result"].total_score <= 100
```

---

*"Six perspectives, one verdict."* 🍷

— Somm.dev Evaluation Pipeline
