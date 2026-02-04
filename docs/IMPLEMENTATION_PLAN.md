# 🍷 Somm.dev - Implementation Plan

> **Step-by-step guide from zero to production**

---

## Phase 1: Foundation (Days 1-2)

### Day 1: Project Setup

#### 1.1 Repository Structure
```bash
# Create project structure
mkdir -p somm.dev/{frontend,backend,docs}
cd somm.dev

# Initialize git
git init
git remote add origin https://github.com/yourusername/somm.dev.git

# Create initial files
touch README.md
mkdir -p frontend/src/{app,components,lib}
mkdir -p backend/app/{api,core,graph,models,prompts,services}
```

#### 1.2 Frontend Setup
```bash
cd frontend

# Initialize Next.js 16
npx create-next-app@latest . --typescript --tailwind --app

# Install dependencies
npm install lucide-react framer-motion
npm install -D @types/node

# Configure for Somm.dev
echo '{
  "name": "somm",
  "version": "0.1.0",
  "private": true
}' > package.json
```

#### 1.3 Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << EOF
fastapi>=0.115.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
motor>=3.4.0
langchain>=0.1.0
langchain-google-genai>=0.0.6
langgraph>=0.0.50
sse-starlette>=2.0.0
python-multipart>=0.0.6
httpx>=0.25.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create pyproject.toml
cat > pyproject.toml << EOF
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
EOF
```

#### 1.4 Environment Configuration
```bash
# Frontend .env.local
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Backend .env
cat > backend/.env << EOF
APP_ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# MongoDB
MONGO_URI=mongodb://localhost:27017/somm
MONGO_DB=somm

# Google Gemini
GOOGLE_API_KEY=your-gemini-api-key

# GitHub OAuth (add later)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
EOF
```

### Day 1 Deliverables
- [ ] Repository initialized
- [ ] Next.js 16 frontend running
- [ ] FastAPI backend running
- [ ] MongoDB connected
- [ ] Environment variables configured

---

## Phase 2: Backend Core (Days 3-5)

### Day 3: FastAPI Foundation

#### 2.1 Core Application
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import evaluate, results, stream, auth
from app.core.config import settings

app = FastAPI(
    title="Somm.dev API",
    description="AI Code Evaluation with Sommelier Sophistication",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(evaluate.router, prefix="/api", tags=["evaluate"])
app.include_router(results.router, prefix="/api", tags=["results"])
app.include_router(stream.router, prefix="/api", tags=["stream"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "somm-api"}
```

#### 2.2 Configuration
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # MongoDB
    MONGO_URI: str
    MONGO_DB: str
    
    # Google
    GOOGLE_API_KEY: str
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2.3 Database Models
```python
# backend/app/models/evaluation.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EvaluationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Evaluation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    repo_url: str
    criteria: str  # basic | hackathon | academic | custom
    status: EvaluationStatus = EvaluationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Day 4: LangGraph Setup

#### 3.1 State Definition
```python
# backend/app/graph/state.py
from typing import Annotated, TypedDict, Optional, List
from pydantic import BaseModel, Field

class SommelierOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    notes: str
    confidence: float = Field(ge=0.0, le=1.0)
    techniques_used: List[str] = Field(default_factory=list)

class FinalEvaluation(BaseModel):
    total_score: int = Field(ge=0, le=100)
    rating: str
    verdict: str
    pairing_suggestions: List[str]
    cellaring_advice: str

class EvaluationState(TypedDict):
    repo_url: str
    repo_context: dict
    evaluation_criteria: str
    user_id: str
    
    marcel_result: Optional[SommelierOutput]
    isabella_result: Optional[SommelierOutput]
    heinrich_result: Optional[SommelierOutput]
    sofia_result: Optional[SommelierOutput]
    laurent_result: Optional[SommelierOutput]
    jeanpierre_result: Optional[FinalEvaluation]
    
    completed_sommeliers: Annotated[List[str], lambda x, y: x + y]
    errors: Annotated[List[str], lambda x, y: x + y]
```

#### 3.2 Base Node
```python
# backend/app/graph/nodes/base.py
from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

class BaseSommelierNode(ABC):
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash",
            temperature=0.3,
            google_api_key=settings.GOOGLE_API_KEY
        )
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    async def evaluate(self, state, config):
        pass
```

#### 3.3 Graph Definition
```python
# backend/app/graph/graph.py
from langgraph.graph import StateGraph, END
from app.graph.state import EvaluationState
from app.graph.nodes.marcel import MarcelNode
# ... other imports

def create_evaluation_graph():
    builder = StateGraph(EvaluationState)
    
    # Add nodes
    builder.add_node("marcel", MarcelNode().evaluate)
    builder.add_node("isabella", IsabellaNode().evaluate)
    builder.add_node("heinrich", HeinrichNode().evaluate)
    builder.add_node("sofia", SofiaNode().evaluate)
    builder.add_node("laurent", LaurentNode().evaluate)
    builder.add_node("jeanpierre", JeanPierreNode().synthesize)
    
    # Parallel edges
    for node in ["marcel", "isabella", "heinrich", "sofia", "laurent"]:
        builder.add_edge("__start__", node)
        builder.add_edge(node, "jeanpierre")
    
    builder.add_edge("jeanpierre", END)
    
    return builder.compile()

evaluation_graph = create_evaluation_graph()
```

### Day 5: API Routes

#### 4.1 Evaluation Endpoint
```python
# backend/app/api/routes/evaluate.py
from fastapi import APIRouter, HTTPException, Depends
from app.services.evaluation_service import EvaluationService
from app.models.evaluation import EvaluationCreate, EvaluationResponse

router = APIRouter()
evaluation_service = EvaluationService()

@router.post("/evaluate", response_model=EvaluationResponse)
async def create_evaluation(
    request: EvaluationCreate,
    current_user: User = Depends(get_current_user)
):
    """Start new code evaluation."""
    
    # Validate criteria
    if request.criteria not in ["basic", "hackathon", "academic", "custom"]:
        raise HTTPException(400, "Invalid criteria")
    
    # Start evaluation
    evaluation_id = await evaluation_service.start(
        repo_url=request.repo_url,
        criteria=request.criteria,
        user_id=current_user.id
    )
    
    return EvaluationResponse(
        evaluation_id=evaluation_id,
        status="pending"
    )
```

#### 4.2 SSE Streaming
```python
# backend/app/api/routes/stream.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.get("/evaluate/{evaluation_id}/stream")
async def stream_evaluation(evaluation_id: str):
    """SSE stream for evaluation progress."""
    
    async def event_generator():
        async for event in evaluation_service.get_progress_stream(evaluation_id):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Phase 2 Deliverables
- [ ] FastAPI application with routes
- [ ] LangGraph evaluation graph
- [ ] 6 sommelier nodes implemented
- [ ] MongoDB integration
- [ ] SSE streaming working
- [ ] API tested with curl/Postman

---

## Phase 3: Frontend (Days 6-8)

### Day 6: Core UI

#### 5.1 Landing Page
```typescript
// frontend/src/app/page.tsx
export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAF4E8] to-[#F7E7CE]">
      <main className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold text-[#722F37] mb-4">
          Somm
        </h1>
        <p className="text-xl text-[#722F37]/80 mb-8">
          AI Code Evaluation with Sommelier Sophistication
        </p>
        <EvaluationForm />
      </main>
    </div>
  );
}
```

#### 5.2 Evaluation Form
```typescript
// frontend/src/components/EvaluationForm.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const CRITERIA_OPTIONS = [
  { value: "basic", label: "Basic Evaluation", icon: "🍷" },
  { value: "hackathon", label: "Gemini 3 Hackathon", icon: "🏆" },
  { value: "academic", label: "Academic Research", icon: "🎓" },
  { value: "custom", label: "Custom", icon: "⚙️" },
];

export function EvaluationForm() {
  const [repoUrl, setRepoUrl] = useState("");
  const [criteria, setCriteria] = useState("basic");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const res = await fetch("${process.env.NEXT_PUBLIC_API_URL}/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: repoUrl, criteria }),
    });

    const data = await res.json();
    router.push(`/evaluate/${data.evaluation_id}`);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <input
        type="url"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        placeholder="https://github.com/user/repo"
        className="w-full px-4 py-3 rounded-lg border border-gray-300"
        required
      />

      <div className="grid grid-cols-2 gap-4">
        {CRITERIA_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => setCriteria(option.value)}
            className={`p-4 rounded-lg border-2 transition-colors ${
              criteria === option.value
                ? "border-[#722F37] bg-[#722F37]/10"
                : "border-gray-200"
            }`}
          >
            <span className="text-2xl">{option.icon}</span>
            <p className="font-medium">{option.label}</p>
          </button>
        ))}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-[#722F37] text-white rounded-lg"
      >
        {loading ? "Analyzing..." : "Begin Evaluation"}
      </button>
    </form>
  );
}
```

### Day 7: Progress Page

```typescript
// frontend/src/app/evaluate/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function EvaluationProgress() {
  const { id } = useParams();
  const [progress, setProgress] = useState({});
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL}/api/evaluate/${id}/stream`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "sommelier_complete") {
        setProgress((prev) => ({
          ...prev,
          [data.sommelier]: data.score,
        }));
      }

      if (data.type === "evaluation_complete") {
        setCompleted(true);
        eventSource.close();
        window.location.href = `/results/${id}`;
      }
    };

    return () => eventSource.close();
  }, [id]);

  return (
    <div className="min-h-screen bg-[#FAF4E8] flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-[#722F37] mb-8">
          Our Sommeliers Are Tasting Your Code...
        </h2>

        <div className="space-y-4">
          {["marcel", "isabella", "heinrich", "sofia", "laurent"].map((name) => (
            <div key={name} className="flex items-center gap-4">
              <span className="capitalize w-24">{name}</span>
              <div className="w-48 h-2 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-[#722F37] rounded-full transition-all"
                  style={{
                    width: progress[name] ? "100%" : "0%",
                  }}
                />
              </div>
              {progress[name] && (
                <span className="text-[#722F37] font-bold">
                  {progress[name]} pts
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Day 8: Results Page

```typescript
// frontend/src/app/results/[id]/page.tsx
async function getResults(id: string) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/evaluate/${id}/result`
  );
  return res.json();
}

export default async function ResultsPage({
  params,
}: {
  params: { id: string };
}) {
  const results = await getResults(params.id);

  return (
    <div className="min-h-screen bg-[#FAF4E8]">
      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-3xl font-bold text-[#722F37] mb-2">
            Tasting Notes
          </h1>
          <p className="text-gray-600">{results.repo_url}</p>
        </header>

        {/* Score */}
        <div className="bg-white rounded-xl p-8 shadow-sm text-center mb-8">
          <div className="text-6xl font-bold text-[#722F37] mb-2">
            {results.total_score}
          </div>
          <div className="text-xl text-[#722F37]/80">
            {results.rating}
          </div>
        </div>

        {/* Sommelier Notes */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-[#722F37]">
            The Sommeliers&apos; Notes
          </h2>
          
          {results.sommeliers.map((sommelier) => (
            <div
              key={sommelier.name}
              className="bg-white rounded-xl p-6 shadow-sm"
            >
              <div className="flex items-center gap-4 mb-4">
                <span className="text-2xl capitalize">{sommelier.name}</span>
                <span className="text-[#722F37] font-bold">
                  {sommelier.score} pts
                </span>
              </div>
              <p className="text-gray-700">{sommelier.notes}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
```

### Phase 3 Deliverables
- [ ] Landing page with criteria selector
- [ ] Evaluation form
- [ ] Progress page with SSE
- [ ] Results page with scores
- [ ] Sommelier notes display
- [ ] Responsive design

---

## Phase 4: Integration & Testing (Days 9-10)

### Day 9: End-to-End Integration

#### 7.1 Full Flow Test
```bash
# Test complete flow
curl -X POST http://localhost:8000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/vercel/next.js",
    "criteria": "basic"
  }'

# Watch SSE stream
curl http://localhost:8000/api/evaluate/{id}/stream

# Get results
curl http://localhost:8000/api/evaluate/{id}/result
```

#### 7.2 Error Handling
- [ ] Invalid GitHub URLs
- [ ] Private repositories
- [ ] Large repositories
- [ ] LLM errors
- [ ] Timeout handling

### Day 10: Polish & Deploy

#### 8.1 Production Build
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
docker build -t somm-backend .
```

#### 8.2 Deployment
- [ ] Deploy backend to Fly.io/Railway
- [ ] Deploy frontend to Vercel
- [ ] Configure environment variables
- [ ] Test production endpoints

---

## Quick Start Commands

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/somm.dev.git
cd somm.dev

# 2. Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 3. Start frontend (new terminal)
cd frontend
npm run dev

# 4. Open browser
open http://localhost:3000
```

---

## Checklist Summary

### Backend
- [ ] FastAPI setup
- [ ] MongoDB connection
- [ ] LangGraph graph
- [ ] 6 sommelier nodes
- [ ] SSE streaming
- [ ] Error handling

### Frontend
- [ ] Next.js 16 setup
- [ ] Landing page
- [ ] Evaluation form
- [ ] Criteria selector
- [ ] Progress page
- [ ] Results page

### Integration
- [ ] API connection
- [ ] SSE client
- [ ] Error boundaries
- [ ] Loading states

### Deployment
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Environment configured
- [ ] Tests passing

---

*"From idea to production in 10 days."* 🍷

— Somm Implementation Guide
