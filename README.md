# 🍷 Somm.dev

> **AI Code Evaluation with Sommelier Sophistication**

Somm.dev is a Multi-Agentic AI code evaluation platform that brings the expertise of a master sommelier to your repositories. Six specialized AI agents analyze your code from every angle—structure, quality, security, innovation—and deliver a comprehensive evaluation report with actionable recommendations.

**Live:** https://www.somm.dev

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/somm.dev.git
cd somm.dev

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm install
npm run dev

# Open browser
open http://localhost:3000
```

---

## 📁 Project Structure

```
somm.dev/
├── frontend/               # Next.js 16 + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities
│   └── package.json
│
├── backend/                # Python FastAPI + LangGraph
│   ├── app/
│   │   ├── api/routes/    # REST API endpoints
│   │   ├── graph/         # LangGraph evaluation pipeline
│   │   │   ├── nodes/     # 6 Sommelier AI agents
│   │   │   ├── state.py   # Graph state definition
│   │   │   └── graph.py   # Graph orchestration
│   │   ├── prompts/       # LangChain prompts
│   │   │   └── criteria/  # 4 evaluation criteria modes
│   │   ├── models/        # Pydantic models
│   │   └── services/      # Business logic
│   ├── requirements.txt
│   └── .env
│
├── docs/                   # Comprehensive documentation
│   ├── ARCHITECTURE.md           # System architecture & LangGraph design
│   ├── EVALUATION_PIPELINE.md    # Multi-agent evaluation flow
│   ├── EVALUATION_CRITERIA.md    # 4 criteria modes (basic/hackathon/academic/custom)
│   ├── IMPLEMENTATION_PLAN.md    # Step-by-step implementation guide
│   └── BRANDING_GUIDE.md         # Brand identity & design system
│
└── README.md
```

---

## 🛠️ Technology Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Utility-first styling
- **Lucide React** - Icon library

### Backend
- **Python 3.12+** - Language
- **FastAPI** - Web framework
- **LangChain** - LLM orchestration framework
- **LangGraph** - Multi-agent workflow orchestration
- **Gemini 3 Flash** - LLM via LangChain
- **MongoDB** - Database
- **SSE** - Real-time streaming

---

## 🎯 The Six Sommeliers

Somm.dev uses **six specialized AI agents** built with LangGraph to evaluate your code:

| Sommelier | Role | Focus Area | Color | Technique |
|-----------|------|------------|-------|-----------|
| 🏛️ **Marcel** | Cellar Master | Structure & Metrics | #8B7355 | Repository organization |
| 🎭 **Isabella** | Wine Critic | Code Quality | #C41E3A | Aesthetics & DX |
| 🔍 **Heinrich** | Quality Inspector | Testing & Security | #2F4F4F | Risk assessment |
| 🌱 **Sofia** | Vineyard Scout | Innovation & Tech | #DAA520 | Growth opportunities |
| 🛠️ **Laurent** | Winemaker | Implementation | #228B22 | Code craftsmanship |
| 🎯 **Jean-Pierre** | Master Sommelier | Final Synthesis | #4169E1 | Final verdict |

**Architecture:** All 5 sommeliers (Marcel, Isabella, Heinrich, Sofia, Laurent) run in parallel using LangGraph's fan-out pattern, then Jean-Pierre synthesizes their results.

---

## 📊 Evaluation Criteria

Somm.dev provides **6 evaluation modes**:

| Mode | Use Case | Description |
|------|----------|-------------|
| **six_sommeliers** | Default evaluation | 6 AI sommelier agents with parallel fan-out pattern |
| **grand_tasting** | Quick evaluation | P0 priority techniques only for faster results |
| **full_techniques** | Comprehensive evaluation | All 75 techniques across 8 categories with deep synthesis |
| **basic** | General code review | Code Quality (25%), Architecture (20%), Documentation (20%), Testing (20%), Security (15%) |
| **hackathon** | Gemini 3 Hackathon judging | Technical (40%), Innovation (30%), Impact (20%), Presentation (10%) |
| **academic** | Research projects | Novelty (25%), Methodology (25%), Reproducibility (20%), Documentation (20%), Impact (10%) |

---

## 🏆 Scoring System

Somm.dev evaluates repositories on a **0-100 point scale**:

| Score | Badge | Description |
|-------|-------|-------------|
| 95-100 | 🏆 **Legendary** | Exceptional quality |
| 90-94 | 🥇 **Grand Cru** | Outstanding |
| 85-89 | 🥈 **Premier Cru** | Excellent |
| 80-84 | 🥉 **Village** | Good |
| 70-79 | 🏅 **Table** | Acceptable |
| 60-69 | 🍷 **House Wine** | Light, enjoyable |
| <60 | ⚠️ **Corked** | Below standards |

---

## 📡 API Endpoints

### Core Evaluation APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/evaluate` | POST | Start code evaluation |
| `/api/evaluate/{id}/stream` | GET | SSE stream for progress |
| `/api/evaluate/{id}/result` | GET | Get evaluation results |
| `/api/history` | GET | User evaluation history |

### Techniques API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/techniques` | GET | List all 75 techniques (filter by category, hat, mode) |
| `/api/techniques/stats` | GET | Get aggregated statistics |
| `/api/techniques/{id}` | GET | Get detailed technique definition |

### Request Example
```bash
curl -X POST http://localhost:8000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "criteria": "basic"
  }'
```

### Response Example
```json
{
  "evaluation_id": "eval_abc123",
  "status": "pending",
  "estimated_time": 30
}
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System architecture, LangGraph design patterns, data flow |
| [EVALUATION_PIPELINE.md](./docs/EVALUATION_PIPELINE.md) | Multi-agent evaluation workflow, node implementations |
| [EVALUATION_CRITERIA.md](./docs/EVALUATION_CRITERIA.md) | 4 evaluation modes with detailed criteria and prompts |
| [IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md) | Step-by-step implementation guide (10-day plan) |
| [BRANDING_GUIDE.md](./docs/BRANDING_GUIDE.md) | Brand identity, terminology, design system |

---

## 🎨 Design System

### Colors
```css
--somm-burgundy: #722F37;      /* Primary */
--somm-champagne: #F7E7CE;     /* Secondary */
--somm-parchment: #FAF4E8;     /* Background */
--somm-cellar: #2E4A3F;        /* Accent */
```

### Typography
- **Headings:** Playfair Display (serif)
- **Body:** Inter (sans-serif)

---

## 🚢 Deployment

### Backend (Fly.io/Railway)
```bash
cd backend
docker build -t somm-backend .
fly deploy
```

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT © 2025 Somm.dev Team

— The Somm.dev Team
