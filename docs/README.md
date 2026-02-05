# 📚 Somm.dev Documentation

> **Complete documentation suite for Somm.dev implementation**

---

## 📖 Document Index

### 🏗️ Architecture & Design

| Document | Description | Key Topics |
|----------|-------------|------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System architecture and LangGraph design | FastAPI structure, LangGraph patterns, state management, data flow |
| [EVALUATION_PIPELINE.md](./EVALUATION_PIPELINE.md) | Multi-agent evaluation pipeline | 6 sommelier nodes, parallel execution, graph definition, SSE streaming |
| [ADR_TEMPLATE.md](./adr/ADR_TEMPLATE.md) | Architecture decision record template | Context, decision, alternatives, consequences |
| [ADR-001-fairthon-alignment.md](./adr/ADR-001-fairthon-alignment.md) | Alignment baseline decisions | Scope, phase order, dependencies |
| [DECISION_LOG.md](./adr/DECISION_LOG.md) | Alignment decision log | Adopted/rejected deltas |

### 🎯 Evaluation System

| Document | Description | Key Topics |
|----------|-------------|------------|
| [EVALUATION_CRITERIA.md](./EVALUATION_CRITERIA.md) | Four evaluation modes | Basic, Hackathon (Gemini 3), Academic, Custom criteria with weights and prompts |
| [BRANDING_GUIDE.md](./BRANDING_GUIDE.md) | Brand identity and design system | Wine metaphors, terminology, colors, typography, voice & tone |

### 🚀 Implementation

| Document | Description | Key Topics |
|----------|-------------|------------|
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Step-by-step implementation guide | 10-day development plan, code examples, deployment instructions |
| [FAIRTHON_ALIGNMENT_PLAN.md](./FAIRTHON_ALIGNMENT_PLAN.md) | Alignment plan | Phased roadmap and scope |

---

## 🗺️ Reading Guide

### For New Team Members
1. Start with [BRANDING_GUIDE.md](./BRANDING_GUIDE.md) - Understand the concept
2. Read [ARCHITECTURE.md](./ARCHITECTURE.md) - Learn system design
3. Review [EVALUATION_PIPELINE.md](./EVALUATION_PIPELINE.md) - Understand the core flow
4. Check [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) - See development roadmap

### For Implementation
1. [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) - Follow day-by-day guide
2. [ARCHITECTURE.md](./ARCHITECTURE.md) - Reference architecture decisions
3. [EVALUATION_PIPELINE.md](./EVALUATION_PIPELINE.md) - Implement graph nodes
4. [EVALUATION_CRITERIA.md](./EVALUATION_CRITERIA.md) - Configure criteria modes

### For API Integration
1. [ARCHITECTURE.md](./ARCHITECTURE.md) - API endpoints section
2. [EVALUATION_PIPELINE.md](./EVALUATION_PIPELINE.md) - SSE streaming
3. [EVALUATION_CRITERIA.md](./EVALUATION_CRITERIA.md) - Criteria selection

---

## 📋 Quick Reference

### Core Concepts
- **Somm.dev**: Multi-Agentic AI code evaluation service
- **6 Sommeliers**: AI agents (Marcel, Isabella, Heinrich, Sofia, Laurent, Jean-Pierre)
- **4 Criteria Modes**: Basic, Hackathon, Academic, Custom
- **Wine Metaphor**: Repository = Bottle, Evaluation = Tasting, History = Cellar

### Technology Stack
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Python 3.12, FastAPI, LangChain, LangGraph, Gemini 3 Flash
- **Database**: MongoDB
- **Streaming**: SSE (Server-Sent Events)

### Scoring Tiers
```
95-100: 🏆 Legendary
90-94:  🥇 Grand Cru
85-89:  🥈 Premier Cru
80-84:  🥉 Village
70-79:  🏅 Table
60-69:  🍷 House Wine
<60:    ⚠️ Corked
```

---

## 🔗 Related Documents

- [Project README](../README.md) - Main project documentation
- [Frontend README](../frontend/README.md) - Frontend-specific docs
- [Backend README](../backend/README.md) - Backend-specific docs

---

*Documentation last updated: February 4, 2026*

— Somm.dev Documentation Team 🍷
