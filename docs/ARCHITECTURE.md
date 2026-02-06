# 🍷 Somm.dev - System Architecture

> **Domain:** somm.dev  
> **Service:** AI Code Evaluation with Sommelier Sophistication  
> **Architecture:** LangChain + LangGraph Powered

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Somm.dev System Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐  │
│  │     Client       │──────▶│   Next.js 16     │──────▶│   FastAPI +      │  │
│  │   (Browser)      │◀──────│   Frontend       │◀──────│   LangGraph      │  │
│  └──────────────────┘      └──────────────────┘      └────────┬─────────┘  │
│         ▲                                                      │            │
│         │                                                      ▼            │
│         │                                            ┌──────────────────┐   │
│         │                                            │   LangGraph      │   │
│         │                                            │   StateGraph     │   │
│         │                                            └────────┬─────────┘   │
│         │                                                     │             │
│         │         ┌───────────────────────────────────────────┼───────────┐ │
│         │         │                                           ▼           │ │
│         │         │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │ │
│         │         │  │  Marcel  │  │ Isabella │  │ Heinrich │  │  ...   │ │ │
│         │         │  │ (Cellar) │  │ (Critic) │  │(Quality) │  │        │ │ │
│         │         │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │ │
│         │         │       └─────────────┴─────────────┴──────────────┘     │ │
│         │         │                          │                             │ │
│         │         │                          ▼                             │ │
│         │         │                ┌──────────────────┐                     │ │
│         │         │                │  Jean-Pierre     │                     │ │
│         │         │                │  (Synthesis)     │                     │ │
│         │         │                └────────┬─────────┘                     │ │
│         │         └─────────────────────────┼───────────────────────────────┘ │
│         │                                   ▼                                 │
│         │                        ┌──────────────────┐                        │
│         │                        │  Gemini 3 Flash  │                        │
│         │                        │  (via LangChain) │                        │
│         │                        └──────────────────┘                        │
│         │                                                                    │
│         └────────────────────────────────────────────────────────────────────┘
│                                     SSE Stream
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 16 + React 19 | UI framework |
| **Backend** | FastAPI + Python 3.12+ | API server |
| **AI Framework** | LangChain + LangGraph | LLM orchestration |
| **LLM** | Gemini 3 Flash (via LangChain) | Code evaluation |
| **Database** | MongoDB | Data persistence |
| **State Management** | LangGraph Checkpoint | Graph state persistence |
| **Streaming** | SSE (Server-Sent Events) | Real-time progress |
| **Auth** | GitHub OAuth + NextAuth.js | User authentication |

---

## 2. LangChain Architecture

### 2.1 LangChain Components

```python
# Core LangChain Components for Somm.dev

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.messages import HumanMessage, SystemMessage

# LLM Configuration (see build_llm() in providers/llm.py)
llm = build_llm(
    provider="gemini",
    model="gemini-3-flash-preview",  # Default model
    temperature=0.7,                  # Default temperature
    max_output_tokens=2048,
)

# Structured Output Schema
class SommelierEvaluation(BaseModel):
    score: int = Field(description="Score from 0-100")
    notes: str = Field(description="Tasting notes in wine metaphor")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    techniques_used: List[str] = Field(description="Evaluation techniques applied")

# Output Parser
parser = JsonOutputParser(pydantic_object=SommelierEvaluation)
```

### 2.2 LangGraph State Management

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph
from langgraph.checkpoint.mongodb import MongoDBSaver

# State Definition (following LangGraph best practices)
class EvaluationState(TypedDict):
    # Input
    repo_url: str
    repo_context: dict
    evaluation_criteria: str  # One of: basic, hackathon, academic, custom
    
    # Parallel sommelier results
    marcel_result: Optional[SommelierEvaluation]
    isabella_result: Optional[SommelierEvaluation]
    heinrich_result: Optional[SommelierEvaluation]
    sofia_result: Optional[SommelierEvaluation]
    laurent_result: Optional[SommelierEvaluation]
    
    # Final synthesis
    jeanpierre_result: Optional[FinalEvaluation]
    
    # Progress tracking
    current_sommelier: str
    progress_percent: int
    errors: Annotated[list, operator.add]

# Graph Definition
def create_evaluation_graph():
    builder = StateGraph(EvaluationState)
    
    # Add nodes for each sommelier
    builder.add_node("marcel", marcel_node)
    builder.add_node("isabella", isabella_node)
    builder.add_node("heinrich", heinrich_node)
    builder.add_node("sofia", sofia_node)
    builder.add_node("laurent", laurent_node)
    builder.add_node("jeanpierre", jeanpierre_node)
    
    # Parallel execution for first 5 sommeliers
    builder.add_edge("__start__", "marcel")
    builder.add_edge("__start__", "isabella")
    builder.add_edge("__start__", "heinrich")
    builder.add_edge("__start__", "sofia")
    builder.add_edge("__start__", "laurent")
    
    # Jean-Pierre waits for all others
    builder.add_edge("marcel", "jeanpierre")
    builder.add_edge("isabella", "jeanpierre")
    builder.add_edge("heinrich", "jeanpierre")
    builder.add_edge("sofia", "jeanpierre")
    builder.add_edge("laurent", "jeanpierre")
    
    builder.add_edge("jeanpierre", "__end__")
    
    return builder.compile()
```

---

## 3. Backend Architecture

### 3.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration (Pydantic Settings)
│   ├── dependencies.py            # FastAPI dependencies
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py               # API dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py           # GitHub OAuth
│   │       ├── evaluate.py       # Evaluation endpoints
│   │       ├── stream.py         # SSE streaming
│   │       ├── results.py        # Results retrieval
│   │       └── history.py        # Evaluation history
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Core configuration
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── logging.py            # Logging setup
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # User models
│   │   ├── evaluation.py         # Evaluation models
│   │   └── results.py            # Results models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github_service.py     # GitHub API integration
│   │   ├── repository_analyzer.py # Repository analysis
│   │   └── sse_manager.py        # SSE connection manager
│   │
│   ├── graph/                    # LangGraph components
│   │   ├── __init__.py
│   │   ├── graph.py              # Main graph definition
│   │   ├── state.py              # State types
│   │   ├── checkpoint.py         # MongoDB checkpointer
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── base.py           # Base node class
│   │       ├── marcel.py         # Cellar Master
│   │       ├── isabella.py       # Wine Critic
│   │       ├── heinrich.py       # Quality Inspector
│   │       ├── sofia.py          # Vineyard Scout
│   │       ├── laurent.py        # Winemaker
│   │       └── jeanpierre.py     # Master Sommelier
│   │
│   ├── prompts/                  # LangChain prompts
│   │   ├── __init__.py
│   │   ├── marcel.py
│   │   ├── isabella.py
│   │   ├── heinrich.py
│   │   ├── sofia.py
│   │   ├── laurent.py
│   │   ├── jeanpierre.py
│   │   └── criteria/             # Evaluation criteria
│   │       ├── basic.py
│   │       ├── hackathon.py
│   │       ├── academic.py
│   │       └── custom.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py         # Input validation
│       └── helpers.py            # Utility functions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_graph.py             # LangGraph tests
│   └── test_api.py               # API tests
│
├── requirements.txt
├── pyproject.toml
└── .env.example
```

### 3.2 LangGraph Node Implementation

```python
# app/graph/nodes/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

class BaseSommelierNode(ABC):
    """Base class for all sommelier nodes following LangChain patterns."""
    
    def __init__(self):
        # LLM is created at evaluate() time via build_llm()
        # Default: gemini-3-flash-preview, temperature=0.7
        self.parser = PydanticOutputParser(pydantic_object=SommelierOutput)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Sommelier name"""
        pass
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Sommelier role description"""
        pass
    
    @abstractmethod
    async def evaluate(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """Execute sommelier evaluation."""
        pass

# app/graph/nodes/marcel.py
from app.graph.nodes.base import BaseSommelierNode
from app.prompts.marcel import get_marcel_prompt
from langchain_core.output_parsers import JsonOutputParser
from app.models.evaluation import SommelierOutput

class MarcelNode(BaseSommelierNode):
    """Cellar Master Marcel - Structure and metrics evaluation."""
    
    name = "marcel"
    role = "Cellar Master"
    
    async def evaluate(self, state, config):
        """Evaluate repository structure using LangChain patterns."""
        
        # Build prompt chain following LCEL
        prompt = get_marcel_prompt(state["evaluation_criteria"])
        parser = JsonOutputParser(pydantic_object=SommelierOutput)
        
        chain = prompt | self.llm | parser
        
        # Execute with error handling
        try:
            result = await chain.ainvoke({
                "repo_context": state["repo_context"],
                "criteria": state["evaluation_criteria"]
            }, config=config)
            
            return {"marcel_result": result}
            
        except Exception as e:
            return {
                "errors": [f"Marcel evaluation failed: {str(e)}"],
                "marcel_result": None
            }
```

---

## 4. Evaluation Criteria System

### 4.1 Four Evaluation Modes

```python
# app/prompts/criteria/types.py
from enum import Enum

class EvaluationCriteria(str, Enum):
    """Four evaluation criteria types."""
    BASIC = "basic"                    # 기본 평가 기준
    HACKATHON = "hackathon"            # 공모전심사 (Gemini 3 Hackathon)
    ACADEMIC = "academic"              # 학술연구
    CUSTOM = "custom"                  # 커스텀

# app/prompts/criteria/base.py
CRITERIA_TEMPLATES = {
    EvaluationCriteria.BASIC: {
        "name": "Basic Evaluation",
        "description": "Standard code quality evaluation",
        "aspects": [
            "code_quality",
            "architecture",
            "documentation",
            "testing",
            "security"
        ]
    },
    
    EvaluationCriteria.HACKATHON: {
        "name": "Gemini 3 Hackathon Judging",
        "description": "Hackathon submission evaluation",
        "aspects": [
            "technical_execution",      # 40%
            "potential_impact",         # 20%
            "innovation_wow",          # 30%
            "presentation_demo"         # 10%
        ],
        "weights": {
            "technical_execution": 0.40,
            "potential_impact": 0.20,
            "innovation_wow": 0.30,
            "presentation_demo": 0.10
        }
    },
    
    EvaluationCriteria.ACADEMIC: {
        "name": "Academic Research",
        "description": "Research project evaluation",
        "aspects": [
            "novelty",
            "methodology",
            "reproducibility",
            "documentation",
            "impact"
        ]
    },
    
    EvaluationCriteria.CUSTOM: {
        "name": "Custom Criteria",
        "description": "User-defined evaluation criteria",
        "aspects": []  # Populated dynamically
    }
}
```

### 4.2 Criteria Integration in Graph

```python
# app/graph/graph.py
from app.prompts.criteria import CRITERIA_TEMPLATES, EvaluationCriteria

def get_criteria_prompt(criteria_type: EvaluationCriteria) -> str:
    """Get evaluation criteria prompt for LangChain."""
    template = CRITERIA_TEMPLATES[criteria_type]
    
    if criteria_type == EvaluationCriteria.HACKATHON:
        return f"""Evaluate this repository as a hackathon submission.
        
Criteria: {template['name']}

Aspects and Weights:
{chr(10).join(f"- {aspect}: {weight*100:.0f}%" for aspect, weight in template['weights'].items())}

Provide detailed evaluation for each aspect.
"""
    
    return f"""Evaluate this repository using {template['name']} criteria.

Key Aspects:
{chr(10).join(f"- {aspect}" for aspect in template['aspects'])}

Provide comprehensive evaluation for each aspect.
"""
```

---

## 5. Data Flow

### 5.1 Evaluation Flow

```
1. User submits repo URL + selects criteria (basic/hackathon/academic/custom)
   ↓
2. FastAPI validates and creates evaluation record in MongoDB
   ↓
3. GitHub service fetches repository context (files, structure, README)
   ↓
4. LangGraph evaluation graph initialized with MongoDB checkpointer
   ↓
5. [Parallel] 5 sommeliers evaluate simultaneously:
   - Marcel (structure) → LLM call
   - Isabella (quality) → LLM call
   - Heinrich (security) → LLM call
   - Sofia (innovation) → LLM call
   - Laurent (implementation) → LLM call
   ↓
6. [Sequential] Jean-Pierre synthesizes all 5 results
   ↓
7. Final result stored in MongoDB
   ↓
8. SSE stream notifies client of completion
   ↓
9. Client fetches and displays tasting notes
```

### 5.2 SSE Streaming Flow

```python
# app/services/sse_manager.py
from typing import Dict, Set
from fastapi import BackgroundTasks

class SSEManager:
    """Manage SSE connections for real-time evaluation updates."""
    
    def __init__(self):
        self.connections: Dict[str, Set] = {}
    
    async def connect(self, evaluation_id: str, queue):
        """Register new SSE connection."""
        if evaluation_id not in self.connections:
            self.connections[evaluation_id] = set()
        self.connections[evaluation_id].add(queue)
    
    async def disconnect(self, evaluation_id: str, queue):
        """Remove SSE connection."""
        if evaluation_id in self.connections:
            self.connections[evaluation_id].discard(queue)
    
    async def broadcast(self, evaluation_id: str, message: dict):
        """Broadcast message to all connected clients."""
        if evaluation_id in self.connections:
            for queue in self.connections[evaluation_id]:
                await queue.put(message)

# LangGraph callback for streaming
class SSECallbackHandler(BaseCallbackHandler):
    """LangChain callback handler for SSE streaming."""
    
    def __init__(self, evaluation_id: str, sse_manager: SSEManager):
        self.evaluation_id = evaluation_id
        self.sse_manager = sse_manager
    
    async def on_chain_start(self, serialized, inputs, **kwargs):
        await self.sse_manager.broadcast(self.evaluation_id, {
            "type": "sommelier_start",
            "sommelier": inputs.get("sommelier", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def on_chain_end(self, outputs, **kwargs):
        await self.sse_manager.broadcast(self.evaluation_id, {
            "type": "sommelier_complete",
            "sommelier": outputs.get("sommelier", "unknown"),
            "score": outputs.get("score"),
            "timestamp": datetime.utcnow().isoformat()
        })
```

---

## 6. Database Schema

### 6.1 MongoDB Collections

```javascript
// evaluations collection
{
  _id: ObjectId,
  evaluation_id: String,           // UUID
  user_id: String,                 // GitHub user ID
  repo_url: String,
  repo_context: {
    owner: String,
    name: String,
    description: String,
    stars: Number,
    language: String,
    file_count: Number,
    structure: Object
  },
  evaluation_criteria: String,     // basic | hackathon | academic | custom
  status: String,                  // pending | running | completed | failed
  
  // LangGraph checkpoint data
  checkpoint: {
    thread_id: String,
    checkpoint_ns: String,
    checkpoint_map: Object
  },
  
  created_at: Date,
  updated_at: Date,
  completed_at: Date
}

// results collection
{
  _id: ObjectId,
  evaluation_id: String,
  
  // Final scores
  total_score: Number,             // 0-100
  rating: String,                  // Legendary | Grand Cru | ... | Corked
  
  // Individual sommelier results
  sommeliers: [{
    name: String,                  // marcel | isabella | ...
    role: String,
    score: Number,
    notes: String,
    confidence: Number,
    techniques_used: [String]
  }],
  
  // Aspect breakdown
  aspects: {
    visual: { score: Number, notes: String },
    aroma: { score: Number, notes: String },
    palate: { score: Number, notes: String },
    finish: { score: Number, notes: String },
    terroir: { score: Number, notes: String },
    vintage: { score: Number, notes: String },
    pairing: { score: Number, notes: String },
    structure: { score: Number, notes: String }
  },
  
  // Recommendations
  pairing_suggestions: [String],
  cellaring_advice: String,
  
  // Metadata
  model: String,                   // gemini-3-flash
  criteria_used: String,
  created_at: Date
}

// users collection
{
  _id: ObjectId,
  github_id: String,
  username: String,
  email: String,
  avatar_url: String,
  preferences: {
    default_criteria: String       // basic | hackathon | academic | custom
  },
  created_at: Date
}
```

---

## 7. API Endpoints

### 7.1 Core Endpoints

```yaml
# Authentication
POST /api/auth/github:
  description: Initiate GitHub OAuth flow
  
GET /api/auth/callback:
  description: OAuth callback handler
  
# Evaluation
POST /api/evaluate:
  description: Start new evaluation
  request:
    repo_url: string
    criteria: enum(basic, hackathon, academic, custom)
    evaluation_mode: enum(six_sommeliers, grand_tasting)  # default: six_sommeliers
  response:
    evaluation_id: string
    status: string
    evaluation_mode: string
    estimated_time: integer  # 30s for six_sommeliers, 60s for grand_tasting
    
GET /api/evaluate/{id}/stream:
  description: SSE stream for progress updates
  content-type: text/event-stream
  
GET /api/evaluate/{id}/result:
  description: Get evaluation results
  response:
    evaluation: object
    
# History
GET /api/history:
  description: Get user's evaluation history
  query:
    page: number
    limit: number
    criteria: string (optional filter)
    
DELETE /api/history/{id}:
  description: Delete evaluation from history
```

---

## 8. Deployment Architecture

### 8.1 Production Setup

```
┌────────────────────────────────────────────────────────────────┐
│                         Production                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐      ┌─────────────────────────────┐  │
│  │   Vercel            │      │   Fly.io / Railway          │  │
│  │   Next.js Frontend  │◀────▶│   FastAPI + LangGraph       │  │
│  │   somm.dev          │      │   api.somm.dev              │  │
│  └─────────────────────┘      └───────────┬─────────────────┘  │
│                                           │                     │
│                                           ▼                     │
│                              ┌─────────────────────────────┐   │
│                              │   MongoDB Atlas             │   │
│                              │   - Evaluations             │   │
│                              │   - Results                 │   │
│                              │   - Checkpoints             │   │
│                              └─────────────────────────────┘   │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 8.2 Environment Variables

```bash
# Backend (.env)
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key

# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/somm
MONGO_DB=somm

# Google Gemini
GOOGLE_API_KEY=your-gemini-api-key

# GitHub
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret

# LangGraph
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langchain-key
LANGCHAIN_PROJECT=somm-dev
```

---

## 9. Best Practices

### 9.1 LangChain Best Practices

1. **Use LCEL for composition**: Build chains using the pipe operator (`|`)
2. **Structured outputs**: Always use Pydantic models with output parsers
3. **Error handling**: Wrap LLM calls in try-except with fallback
4. **Async everywhere**: Use `ainvoke` for all LLM calls
5. **Streaming**: Implement callbacks for real-time updates
6. **Caching**: Use LangChain caching for repeated prompts

### 9.2 LangGraph Best Practices

1. **TypedDict state**: Define clear state schemas
2. **Checkpointing**: Use MongoDB checkpointer for persistence
3. **Parallel execution**: Use fan-out for independent nodes
4. **Error aggregation**: Collect errors without failing entire graph
5. **Streaming callbacks**: Implement for progress tracking
6. **State immutability**: Treat state as immutable, return updates

### 9.3 FastAPI Best Practices

1. **Dependency injection**: Use FastAPI dependencies for shared resources
2. **Pydantic models**: Validate all inputs and outputs
3. **Async endpoints**: Make all I/O-bound endpoints async
4. **Background tasks**: Use BackgroundTasks for non-critical operations
5. **Exception handlers**: Global exception handlers for consistent errors

---

## 10. Next Steps

1. **Setup Development Environment**: Install dependencies, configure env
2. **Implement Graph Nodes**: Create all 6 sommelier nodes
3. **Build API Routes**: Implement evaluation and streaming endpoints
4. **Frontend Integration**: Connect Next.js to FastAPI backend
5. **Testing**: Unit tests for nodes, integration tests for graph
6. **Deployment**: Deploy to Fly.io/Railway + Vercel

---

*"Every codebase has terroir. We're here to taste it."* 🍷

— Somm.dev Team
