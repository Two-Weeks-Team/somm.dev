# Somm.dev Comprehensive Implementation Plan

> **Project:** Somm.dev - AI Code Evaluation with Sommelier Sophistication  
> **Domain:** somm.dev  
> **Timeline:** 4-6 weeks (Feb 4 - Mar 18, 2026)  
> **Status:** Ready for Implementation

---

## Context

### Original Request
Create comprehensive implementation documentation for Somm.dev, adapting existing GitSomm plans to the new Somm branding. Include 6 Sommelier AI agents, 75 evaluation techniques mapping, House Wine tier (60-69), and implementation-ready documentation.

### Interview Summary

**Key Discussions:**
- Deployment: Frontend on Vercel, Backend on Self-hosted Docker
- AI Models: Gemini 3 Pro (quality) + Flash (speed) - user selectable
- Authentication: GitHub OAuth only
- 75 Techniques: Dynamic selection - AI chooses relevant techniques per repo
- Timeline: Full feature implementation - 4-6 weeks

**Research Findings:**
- Current somm.dev has basic landing page and backend skeleton
- House Wine tier (60-69) already in UI
- Branding guide already updated for Somm

### Source Documents Analyzed
1. `GITSOMM_COMPREHENSIVE_PLAN.md` (1423 lines) - Development plan
2. `GITSOMM_PRODUCTION_MASTERPLAN.md` (1562 lines) - Production architecture
3. `SOMM_DEV_BRANDING.md` (348 lines) - Branding guide

---

## Work Objectives

### Core Objective
Build a production-ready AI code evaluation platform themed around wine sommeliers, where 6 specialized AI agents analyze GitHub repositories and deliver comprehensive "tasting notes" with scores and recommendations.

### Concrete Deliverables
- 15 documentation files (architecture, API, database, agents, techniques, etc.)
- 6 Sommelier AI agents with distinct personalities
- 75 evaluation techniques with wine metaphor mapping
- Full evaluation pipeline with Gemini 3 Pro/Flash
- Wine-themed UI components (evaluate, report, history pages)
- GitHub OAuth authentication
- SSE streaming for real-time progress
- MongoDB + Redis infrastructure

### Definition of Done
- [ ] All 15 documentation files created and reviewed
- [ ] 6 sommeliers implemented and tested
- [ ] End-to-end evaluation flow working
- [ ] SSE streaming delivers real-time updates
- [ ] User can authenticate, submit repo, view results

### Must Have
- 6 Sommelier AI agents (Marcel, Isabella, Heinrich, Sofia, Laurent, Jean-Pierre)
- Wine-themed scoring (0-100 with Legendary→Corked tiers)
- House Wine tier (60-69)
- Dynamic technique selection (15-25 of 75 techniques per evaluation)
- GitHub OAuth authentication
- Real-time progress streaming (SSE)

### Must NOT Have (Guardrails)
- Multi-repo comparison (v1 scope)
- Team/organization features (v1 scope)
- Payment/billing system (free tier only for v1)
- i18n/localization (English only for v1)
- Private repo access without user PAT
- Raw code storage (security risk)
- Over-abstraction of sommelier logic
- Premature microservice architecture

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (needs setup)
- **User wants tests**: Manual verification for documentation, integration tests for code
- **Framework**: pytest (backend), Playwright (e2e)

### Manual Execution Verification

Each documentation TODO includes verification:
- Document renders correctly in Markdown
- All diagrams display properly
- Cross-references link correctly
- Examples are accurate and executable

Each implementation TODO includes:
- API endpoint testing via curl/httpie
- SSE testing via EventSource
- Frontend verification via Playwright browser

---

## Task Flow

```
PHASE 1: Foundation Docs
TODO 1 (ARCHITECTURE) → TODO 2 (DATABASE) + TODO 3 (API) → TODO 4 (SOMMELIERS)

PHASE 2: Technical Specs
TODO 4 → TODO 5 (75_TECHNIQUES) → TODO 6 (GEMINI) + TODO 7 (SSE) + TODO 8 (GITHUB)

PHASE 3: Implementation Guides
TODO 6 → TODO 9 (FRONTEND) + TODO 10 (PIPELINE) + TODO 11 (SCORING) + TODO 12 (ERRORS)

PHASE 4: Deployment
TODO 13 (DEPLOYMENT) + TODO 14 (SECURITY) + TODO 15 (README)

PHASE 5: Implementation
TODO 16-20 (Backend + Frontend + Infrastructure)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 2, 3 | DATABASE and API can be written simultaneously after ARCHITECTURE |
| B | 6, 7, 8 | GEMINI, SSE, GITHUB integrations are independent specs |
| C | 9, 10, 11, 12 | Implementation guides can be written in parallel |
| D | 13, 14, 15 | Deployment docs are independent |
| E | 17, 18, 19 | Backend routes, frontend pages, auth can be parallelized |

---

## TODOs

### Phase 1: Foundation (Week 1)

- [ ] 1. Create ARCHITECTURE.md

  **What to do**:
  - System architecture diagram using Mermaid
  - Component responsibilities (Frontend, Backend, MongoDB, Redis)
  - Data flow: submit → analyze → report
  - Infrastructure: Vercel ↔ Docker ↔ MongoDB ↔ Redis

  **Must NOT do**:
  - Over-complicate with microservices (monolith first)
  - Include implementation details (that's for code)

  **Parallelizable**: NO (foundation for all other docs)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:30-86` - System architecture section
  - `GITSOMM_COMPREHENSIVE_PLAN.md:154-178` - System overview
  - Current repo structure: `somm.dev/frontend/`, `somm.dev/backend/`

  **Acceptance Criteria**:
  - [ ] Architecture diagram renders correctly in GitHub
  - [ ] All components documented with responsibilities
  - [ ] Data flow covers happy path + error scenarios
  - [ ] Mermaid diagrams validated: `npx mermaid-cli validate docs/ARCHITECTURE.md`

  **Commit**: YES
  - Message: `docs: add system architecture documentation`
  - Files: `docs/ARCHITECTURE.md`

---

- [ ] 2. Create DATABASE_SCHEMA.md

  **What to do**:
  - MongoDB collections: `somm_users`, `somm_evaluations`, `somm_results`, `somm_events`
  - Redis data structures: rate limiting, job queue, pub/sub, cache
  - Index definitions for query optimization
  - TTL policies for ephemeral data

  **Must NOT do**:
  - Create overly normalized schemas (MongoDB is document-oriented)
  - Skip index definitions

  **Parallelizable**: YES (with TODO 3)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:1039-1196` - Database schemas
  - `docs/BRANDING_GUIDE.md:329-336` - Collection naming conventions

  **Acceptance Criteria**:
  - [ ] All collections have complete schema definitions
  - [ ] Indexes defined for all query patterns (list each index)
  - [ ] Redis key patterns documented with TTLs
  - [ ] Example documents provided for each collection

  **Commit**: YES
  - Message: `docs: add database schema documentation`
  - Files: `docs/DATABASE_SCHEMA.md`

---

- [ ] 3. Create API_SPECIFICATION.md

  **What to do**:
  - OpenAPI 3.0 spec format
  - Endpoints: `/api/evaluate`, `/api/report/:id`, `/api/history`, `/api/stream/:id`, `/api/sommeliers`
  - Request/response schemas (Pydantic models)
  - Error codes with wine-themed messages
  - Rate limiting documentation

  **Must NOT do**:
  - Deviate from RESTful conventions
  - Skip error response documentation

  **Parallelizable**: YES (with TODO 2)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:1199-1284` - API specifications
  - `backend/main.py` - Existing endpoint patterns

  **Acceptance Criteria**:
  - [ ] All endpoints have full OpenAPI schema definitions
  - [ ] Error responses documented with examples
  - [ ] Rate limits specified per endpoint
  - [ ] Authentication requirements documented

  **Commit**: YES
  - Message: `docs: add API specification documentation`
  - Files: `docs/API_SPECIFICATION.md`

---

- [ ] 4. Create SOMMELIER_AGENTS.md

  **What to do**:
  - 6 sommelier definitions with full personas
  - Wine metaphor mapping for each agent
  - Prompt templates for Gemini 3
  - Output schemas (structured JSON)
  - Technique assignment per sommelier

  **Sommeliers**:
  | # | Name | Role | Focus | Color |
  |---|------|------|-------|-------|
  | 1 | Marcel | Cellar Master | Structure, metrics, organization | #8B7355 |
  | 2 | Isabella | Wine Critic | Code quality, patterns, DX | #C41E3A |
  | 3 | Heinrich | Quality Inspector | Security, testing, reliability | #2F4F4F |
  | 4 | Sofia | Vineyard Scout | Innovation, tech stack, potential | #DAA520 |
  | 5 | Laurent | Winemaker | Implementation, performance | #228B22 |
  | 6 | Jean-Pierre | Master Sommelier | Synthesis, final verdict | #4169E1 |

  **Must NOT do**:
  - Create generic prompts (each must have distinct personality)
  - Skip output schema definitions

  **Parallelizable**: NO (required for TODO 5)

  **References**:
  - `GITSOMM_COMPREHENSIVE_PLAN.md:420-455` - Sommelier requirements
  - `GITSOMM_COMPREHENSIVE_PLAN.md:1051-1194` - Prompt templates
  - `docs/BRANDING_GUIDE.md:108-147` - Current sommelier definitions

  **Acceptance Criteria**:
  - [ ] All 6 sommeliers have complete personas (name, role, focus, personality)
  - [ ] Prompt templates include wine terminology
  - [ ] Output schemas defined for Gemini structured output
  - [ ] Example outputs provided for each sommelier

  **Commit**: YES
  - Message: `docs: add sommelier agents documentation`
  - Files: `docs/SOMMELIER_AGENTS.md`

---

### Phase 2: Technical Specifications (Week 2)

- [ ] 5. Create 75_TECHNIQUES.md

  **What to do**:
  - All 75 evaluation techniques with unique IDs
  - Wine phase mapping (Visual, Aroma, Palate, Finish, Terroir, Vintage, Pairing, Structure, Cellaring)
  - Dynamic selection algorithm documentation
  - Technique-to-sommelier assignment matrix
  - YAML template format for technique definitions

  **Wine Phase → Technique Category Mapping**:
  | Wine Phase | Tech Category | Count |
  |------------|---------------|-------|
  | Visual | Problem Analysis | 10 |
  | Aroma | User Centricity | 12 |
  | Palate | Feasibility | 8 |
  | Finish | Risk Analysis | 8 |
  | Terroir | Presentation | 5 |
  | Vintage | Synthesis | 6 |
  | Pairing | Opportunity | 10 |
  | Structure | Innovation | 13 |
  | Cellaring | Special | 3 |

  **Dynamic Selection Algorithm**:
  ```
  1. Analyze repo metadata (language, size, age, dependencies)
  2. Score technique relevance (0-1) based on context
  3. Select top 15-25 techniques per evaluation
  4. Distribute across sommeliers by expertise mapping
  ```

  **Must NOT do**:
  - Create techniques without wine mappings
  - Skip selection algorithm documentation

  **Parallelizable**: NO (depends on TODO 4)

  **References**:
  - `GITSOMM_COMPREHENSIVE_PLAN.md:458-484` - Technique mapping
  - `GITSOMM_COMPREHENSIVE_PLAN.md:1221-1315` - All 75 techniques list

  **Acceptance Criteria**:
  - [ ] All 75 techniques documented with ID, name, description, wine mapping
  - [ ] Selection algorithm specified with pseudocode
  - [ ] Technique-sommelier matrix provided
  - [ ] YAML template format defined and validated

  **Commit**: YES
  - Message: `docs: add 75 evaluation techniques documentation`
  - Files: `docs/75_TECHNIQUES.md`

---

- [ ] 6. Create GEMINI_INTEGRATION.md

  **What to do**:
  - Gemini 3 Pro vs Flash selection criteria
  - Structured output schemas for each sommelier
  - Rate limiting gateway with circuit breaker
  - Retry logic with exponential backoff
  - Token budget management
  - Prompt versioning strategy

  **Model Selection Criteria**:
  | Criteria | Gemini 3 Pro | Gemini 3 Flash |
  |----------|--------------|----------------|
  | Context | 1M tokens | 1M tokens |
  | Cost | $2/M input | $0.5/M input |
  | Speed | Slower | Faster |
  | Quality | Higher | Good |
  | Use when | Large repos (>50 files), detailed analysis | Quick scans, high volume |

  **Must NOT do**:
  - Skip error handling documentation
  - Ignore rate limit considerations

  **Parallelizable**: YES (with TODO 7, 8)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:208-247` - Gemini Gateway
  - `GITSOMM_COMPREHENSIVE_PLAN.md:277-300` - Gemini integration

  **Acceptance Criteria**:
  - [ ] Model selection logic documented with decision tree
  - [ ] Structured output schemas defined per sommelier
  - [ ] Error handling and retry logic specified
  - [ ] Circuit breaker parameters documented

  **Commit**: YES
  - Message: `docs: add Gemini integration documentation`
  - Files: `docs/GEMINI_INTEGRATION.md`

---

- [ ] 7. Create SSE_STREAMING.md

  **What to do**:
  - Server-Sent Events specification
  - Event types: `sommelier_start`, `sommelier_complete`, `progress`, `complete`, `error`
  - Heartbeat mechanism (15-second intervals)
  - Client reconnection with exponential backoff
  - Polling fallback for environments without SSE

  **Event Format**:
  ```json
  {
    "type": "sommelier_start",
    "sommelier": "marcel",
    "timestamp": "2026-02-04T10:30:00Z",
    "data": {}
  }
  ```

  **Must NOT do**:
  - Skip heartbeat mechanism (connections will timeout)
  - Ignore fallback strategy

  **Parallelizable**: YES (with TODO 6, 8)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:715-764` - SSE implementation
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:1240-1262` - Stream endpoint spec

  **Acceptance Criteria**:
  - [ ] All event types documented with TypeScript interfaces
  - [ ] Heartbeat spec defined (interval, timeout)
  - [ ] Reconnection strategy specified with backoff parameters
  - [ ] Polling fallback endpoint documented

  **Commit**: YES
  - Message: `docs: add SSE streaming documentation`
  - Files: `docs/SSE_STREAMING.md`

---

- [ ] 8. Create GITHUB_INTEGRATION.md

  **What to do**:
  - GitHub OAuth flow with NextAuth.js
  - Repository access patterns (API + optional clone)
  - Rate limit handling (5000/hour authenticated)
  - File tree extraction algorithm
  - Language detection method
  - Dependency parsing (package.json, requirements.txt, go.mod, etc.)

  **Must NOT do**:
  - Store GitHub tokens insecurely
  - Ignore rate limit handling

  **Parallelizable**: YES (with TODO 6, 7)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:155-175` - GitHub OAuth
  - `GITSOMM_COMPREHENSIVE_PLAN.md:774-781` - GitHub integration

  **Acceptance Criteria**:
  - [ ] OAuth flow documented with sequence diagram
  - [ ] API endpoints for repo analysis listed with rate limits
  - [ ] File tree extraction algorithm documented
  - [ ] Dependency parser file patterns documented

  **Commit**: YES
  - Message: `docs: add GitHub integration documentation`
  - Files: `docs/GITHUB_INTEGRATION.md`

---

### Phase 3: Implementation Guides (Week 3)

- [ ] 9. Create FRONTEND_COMPONENTS.md

  **What to do**:
  - Component specifications with TypeScript props interfaces
  - Wine-themed styling guide (CSS variables)
  - Animation specifications (Framer Motion)
  - Responsive design breakpoints
  - Accessibility requirements (ARIA)

  **Component List**:
  | Component | Purpose | Location |
  |-----------|---------|----------|
  | `RepoCard` | Display repository for selection | `somm-evaluate/` |
  | `RepoInput` | GitHub URL input with validation | `somm-evaluate/` |
  | `AnalysisProgress` | Loading animation during eval | `somm-progress/` |
  | `SommelierNote` | Individual sommelier output | `somm-report/` |
  | `PointsBadge` | Score display (0-100) | `somm-report/` |
  | `AspectRadar` | Wine aspects visualization | `somm-report/` |
  | `HistoryCard` | Past evaluation summary | `somm-history/` |
  | `HistoryShelf` | Repository history view | `somm-history/` |

  **Must NOT do**:
  - Create components without TypeScript interfaces
  - Skip accessibility considerations

  **Parallelizable**: YES (with TODO 10, 11, 12)

  **References**:
  - `GITSOMM_COMPREHENSIVE_PLAN.md:493-539` - Component specs
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:477-621` - UI components
  - `docs/BRANDING_GUIDE.md:176-208` - Color palette

  **Acceptance Criteria**:
  - [ ] All components have TypeScript interfaces
  - [ ] CSS variables reference branding guide
  - [ ] Animation specs include duration and easing
  - [ ] Responsive breakpoints documented (sm, md, lg, xl)

  **Commit**: YES
  - Message: `docs: add frontend components documentation`
  - Files: `docs/FRONTEND_COMPONENTS.md`

---

- [ ] 10. Create EVALUATION_PIPELINE.md

  **What to do**:
  - Complete end-to-end flow documentation
  - Job queue architecture (Redis + ARQ/Celery)
  - Worker implementation pattern
  - Progress publishing mechanism (Redis Pub/Sub)
  - Result aggregation and synthesis by Jean-Pierre
  - Caching strategy (by repo@sha)

  **Pipeline Flow**:
  ```
  1. User submits repo URL
  2. API creates job in MongoDB, enqueues in Redis
  3. Worker picks up job
  4. Fetch repo context (GitHub API)
  5. Dynamic technique selection (15-25 techniques)
  6. Execute 6 sommeliers in parallel (bounded to 3 concurrent Gemini calls)
  7. Publish progress via Redis Pub/Sub
  8. Jean-Pierre synthesizes final result
  9. Store result in MongoDB
  10. Publish completion event
  11. SSE delivers to client
  ```

  **Must NOT do**:
  - Skip error handling at any pipeline stage
  - Ignore caching strategy

  **Parallelizable**: YES (with TODO 9, 11, 12)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:313-390` - Evaluation pipeline
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:392-426` - Caching

  **Acceptance Criteria**:
  - [ ] All pipeline stages documented with error handling
  - [ ] Job state machine defined (pending, running, complete, failed)
  - [ ] Caching key format specified (repo@sha:prompt_version:technique_version)
  - [ ] Retry policies defined per stage

  **Commit**: YES
  - Message: `docs: add evaluation pipeline documentation`
  - Files: `docs/EVALUATION_PIPELINE.md`

---

- [ ] 11. Create SCORING_SYSTEM.md

  **What to do**:
  - 0-100 point scale breakdown
  - Badge tier definitions (Legendary → Corked)
  - Score calculation algorithm
  - Aspect weighting
  - Confidence adjustment formula

  **Scoring Tiers**:
  | Score | Badge | Emoji | Description |
  |-------|-------|-------|-------------|
  | 95-100 | Legendary | 🏆 | Exceptional, rare quality |
  | 90-94 | Grand Cru | 🥇 | Outstanding |
  | 85-89 | Premier Cru | 🥈 | Excellent |
  | 80-84 | Village | 🥉 | Good |
  | 70-79 | Table | 🏅 | Acceptable |
  | 60-69 | House Wine | 🍷 | Light, enjoyable |
  | <60 | Corked | ⚠️ | Below standards |

  **Calculation Formula**:
  ```
  sommelier_scores = [marcel.score, isabella.score, heinrich.score, sofia.score, laurent.score]
  weighted_avg = sum(score * weight) / sum(weights)
  confidence_factor = successful_techniques / attempted_techniques
  final_score = weighted_avg * confidence_factor
  ```

  **Must NOT do**:
  - Skip House Wine tier (60-69) - explicitly required
  - Create arbitrary scoring without formula

  **Parallelizable**: YES (with TODO 9, 10, 12)

  **References**:
  - `GITSOMM_COMPREHENSIVE_PLAN.md:1196-1219` - Wine terminology
  - `docs/BRANDING_GUIDE.md:150-172` - Current scoring system
  - `frontend/src/app/page.tsx:79-115` - Current UI implementation

  **Acceptance Criteria**:
  - [ ] All 7 tiers documented with criteria
  - [ ] Calculation formula specified with weights
  - [ ] Edge cases documented (partial failures, low confidence)
  - [ ] Example calculations provided

  **Commit**: YES
  - Message: `docs: add scoring system documentation`
  - Files: `docs/SCORING_SYSTEM.md`

---

- [ ] 12. Create ERROR_HANDLING.md

  **What to do**:
  - Wine-themed error messages
  - Error code taxonomy (HTTP status → wine term)
  - Retry strategies per error type
  - Graceful degradation patterns
  - User-facing vs developer error messages

  **Error Categories**:
  | Code | Wine Term | Meaning | User Message |
  |------|-----------|---------|--------------|
  | 400 | Corked | Invalid input | "This bottle appears corked. Check your repository URL." |
  | 401 | No Invitation | Auth required | "You'll need an invitation to enter the tasting room." |
  | 404 | Empty Cellar | Not found | "This vintage doesn't appear to be in our cellar." |
  | 429 | Overconsumption | Rate limit | "Please pace yourself—the cellar needs time to restock." |
  | 500 | Spoiled Batch | Server error | "Something went wrong in the cellar. Our sommeliers are investigating." |
  | 503 | Cellar Closed | Service unavailable | "The tasting room is temporarily closed for maintenance." |

  **Must NOT do**:
  - Expose internal error details to users
  - Skip retry policies

  **Parallelizable**: YES (with TODO 9, 10, 11)

  **References**:
  - `docs/BRANDING_GUIDE.md:243-250` - Tone by context

  **Acceptance Criteria**:
  - [ ] All HTTP codes mapped to wine terms
  - [ ] Retry policy per error type defined (retryable vs terminal)
  - [ ] User messages are helpful and on-brand
  - [ ] Developer error logging format specified

  **Commit**: YES
  - Message: `docs: add error handling documentation`
  - Files: `docs/ERROR_HANDLING.md`

---

### Phase 4: Deployment & Operations (Week 4)

- [ ] 13. Create DEPLOYMENT.md

  **What to do**:
  - Docker configuration (Dockerfile, docker-compose)
  - Vercel configuration (vercel.json)
  - Environment variable documentation
  - CI/CD pipeline (GitHub Actions)
  - Health check endpoints
  - Rollback procedures

  **Environment Variables**:
  ```bash
  # Frontend (Vercel)
  NEXTAUTH_SECRET=
  NEXTAUTH_URL=https://www.somm.dev
  GITHUB_CLIENT_ID=
  GITHUB_CLIENT_SECRET=
  NEXT_PUBLIC_API_URL=https://api.somm.dev

  # Backend (Docker)
  GEMINI_API_KEY=
  GITHUB_TOKEN=
  MONGO_URI=
  REDIS_URL=
  SOMM_ENV=production
  SOMM_LOG_LEVEL=info
  ```

  **Must NOT do**:
  - Include actual secrets in documentation
  - Skip health check documentation

  **Parallelizable**: YES (with TODO 14, 15)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:1289-1342` - Environment vars
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:1428-1465` - Deployment checklist

  **Acceptance Criteria**:
  - [ ] Dockerfile documented with all stages
  - [ ] docker-compose.yml provided for local development
  - [ ] All env vars documented with descriptions and required/optional status
  - [ ] GitHub Actions workflow specified

  **Commit**: YES
  - Message: `docs: add deployment documentation`
  - Files: `docs/DEPLOYMENT.md`

---

- [ ] 14. Create SECURITY.md

  **What to do**:
  - Secrets scanning (prevent API key leaks in repos)
  - Input sanitization (no raw code storage)
  - Rate limiting implementation details
  - CORS configuration
  - CSP headers
  - Max file/repo size limits
  - OAuth security best practices

  **Security Guardrails**:
  | Risk | Mitigation |
  |------|------------|
  | Secrets in repos | Regex scan before LLM, never store raw code |
  | XSS | CSP headers, output sanitization |
  | DoS | Rate limiting (10 req/hr), max repo size (100MB) |
  | Token theft | httpOnly cookies, short-lived tokens |
  | API abuse | Per-user limits, circuit breaker |

  **Must NOT do**:
  - Skip rate limiting documentation
  - Ignore secrets handling

  **Parallelizable**: YES (with TODO 13, 15)

  **References**:
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:1469-1510` - Risk mitigation
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:877-883` - Security audit checklist

  **Acceptance Criteria**:
  - [ ] All security measures documented with implementation details
  - [ ] Rate limiting spec complete with Redis key format
  - [ ] Secrets regex patterns provided
  - [ ] CORS and CSP configs provided

  **Commit**: YES
  - Message: `docs: add security documentation`
  - Files: `docs/SECURITY.md`

---

- [ ] 15. Update README.md

  **What to do**:
  - Comprehensive project overview
  - Quick start guide (frontend + backend)
  - Architecture diagram (embed from ARCHITECTURE.md)
  - API overview with examples
  - The Six Sommeliers section (update)
  - Scoring system section (verify House Wine tier)
  - Contribution guidelines
  - License information

  **Must NOT do**:
  - Remove existing branding elements
  - Skip quick start instructions

  **Parallelizable**: YES (with TODO 13, 14)

  **References**:
  - Current: `README.md` - Existing structure to preserve
  - `GITSOMM_COMPREHENSIVE_PLAN.md:1390-1422` - Quick reference
  - `docs/BRANDING_GUIDE.md` - Messaging guidelines

  **Acceptance Criteria**:
  - [ ] README reflects complete system
  - [ ] Quick start works for new developers (verified by running locally)
  - [ ] All major features documented
  - [ ] Links to all documentation files

  **Commit**: YES
  - Message: `docs: update README with comprehensive project overview`
  - Files: `README.md`

---

### Phase 5: Implementation (Weeks 4-6)

- [ ] 16. Implement Backend Sommeliers

  **What to do**:
  - Create `backend/app/sommeliers/` directory structure
  - Implement `BaseSommelier` abstract class
  - Implement all 6 sommelier agents with personas
  - Create Gemini gateway with rate limiting
  - Add structured output schemas (Pydantic)

  **Files to create**:
  - `backend/app/sommeliers/__init__.py`
  - `backend/app/sommeliers/base.py`
  - `backend/app/sommeliers/marcel.py`
  - `backend/app/sommeliers/isabella.py`
  - `backend/app/sommeliers/heinrich.py`
  - `backend/app/sommeliers/sofia.py`
  - `backend/app/sommeliers/laurent.py`
  - `backend/app/sommeliers/jeanpierre.py`
  - `backend/app/services/gemini_gateway.py`
  - `backend/app/schemas/sommelier_output.py`

  **Must NOT do**:
  - Create generic prompts without personality
  - Skip structured output validation

  **Parallelizable**: NO (foundation for evaluation pipeline)

  **References**:
  - `docs/SOMMELIER_AGENTS.md` - Agent specifications (TODO 4)
  - `docs/GEMINI_INTEGRATION.md` - Gateway patterns (TODO 6)
  - `GITSOMM_PRODUCTION_MASTERPLAN.md:279-307` - Sommelier implementation

  **Acceptance Criteria**:
  - [ ] All 6 sommeliers instantiate without errors
  - [ ] Each sommelier returns structured output matching schema
  - [ ] Gemini gateway handles rate limiting correctly
  - [ ] Unit tests pass: `pytest backend/tests/test_sommeliers.py`

  **Commit**: YES
  - Message: `feat(backend): implement 6 sommelier AI agents`
  - Files: `backend/app/sommeliers/`, `backend/app/services/gemini_gateway.py`

---

- [ ] 17. Implement API Routes

  **What to do**:
  - `/api/evaluate` - Start evaluation (POST)
  - `/api/report/:id` - Get results (GET)
  - `/api/history` - User history (GET)
  - `/api/stream/:id` - SSE progress (GET)
  - `/api/sommeliers` - Sommelier info (GET)

  **Files to create**:
  - `backend/app/api/__init__.py`
  - `backend/app/api/routes/__init__.py`
  - `backend/app/api/routes/evaluate.py`
  - `backend/app/api/routes/report.py`
  - `backend/app/api/routes/history.py`
  - `backend/app/api/routes/stream.py`
  - `backend/app/api/routes/sommeliers.py`
  - `backend/app/api/deps.py` (dependencies)

  **Must NOT do**:
  - Skip authentication middleware
  - Return raw errors to users

  **Parallelizable**: YES (with TODO 18, 19)

  **References**:
  - `docs/API_SPECIFICATION.md` - API contracts (TODO 3)
  - `docs/ERROR_HANDLING.md` - Error responses (TODO 12)

  **Acceptance Criteria**:
  - [ ] All endpoints respond with correct schemas
  - [ ] Authentication required where specified
  - [ ] Error responses match ERROR_HANDLING.md
  - [ ] API tests pass: `pytest backend/tests/test_api.py`

  **Commit**: YES
  - Message: `feat(backend): implement core API routes`
  - Files: `backend/app/api/`

---

- [ ] 18. Implement Frontend Pages

  **What to do**:
  - Evaluate page (repo submission form)
  - Report page (results display)
  - History page (past evaluations)
  - Analysis progress modal

  **Files to create**:
  - `frontend/src/app/evaluate/page.tsx`
  - `frontend/src/app/report/[id]/page.tsx`
  - `frontend/src/app/history/page.tsx`
  - `frontend/src/components/somm-evaluate/RepoInput.tsx`
  - `frontend/src/components/somm-progress/AnalysisProgress.tsx`
  - `frontend/src/components/somm-report/SommelierNote.tsx`
  - `frontend/src/components/somm-report/PointsBadge.tsx`
  - `frontend/src/components/somm-report/AspectRadar.tsx`
  - `frontend/src/components/somm-history/HistoryCard.tsx`

  **Must NOT do**:
  - Break existing landing page
  - Skip loading/error states

  **Parallelizable**: YES (with TODO 17, 19)

  **References**:
  - `docs/FRONTEND_COMPONENTS.md` - Component specs (TODO 9)
  - `docs/BRANDING_GUIDE.md` - Styling guide
  - `frontend/src/app/page.tsx` - Current landing page patterns

  **Acceptance Criteria**:
  - [ ] All pages render without errors
  - [ ] Components use wine theme CSS variables
  - [ ] Responsive on mobile (test at 375px width)
  - [ ] E2E tests pass: `npx playwright test`

  **Commit**: YES
  - Message: `feat(frontend): implement evaluate, report, and history pages`
  - Files: `frontend/src/app/`, `frontend/src/components/`

---

- [ ] 19. Implement Authentication

  **What to do**:
  - NextAuth.js with GitHub provider
  - Protected routes middleware
  - User session management
  - MongoDB user storage

  **Files to create**:
  - `frontend/src/app/api/auth/[...nextauth]/route.ts`
  - `frontend/src/lib/auth.ts`
  - `frontend/src/middleware.ts`
  - `frontend/src/types/next-auth.d.ts` (type extensions)

  **Must NOT do**:
  - Store tokens insecurely
  - Skip session validation

  **Parallelizable**: YES (with TODO 17, 18)

  **References**:
  - `docs/GITHUB_INTEGRATION.md` - OAuth flow (TODO 8)
  - `docs/SECURITY.md` - Token handling (TODO 14)

  **Acceptance Criteria**:
  - [ ] GitHub OAuth login works end-to-end
  - [ ] Protected routes redirect to login
  - [ ] User session persists across page refreshes
  - [ ] Auth tests pass: `npx playwright test e2e/auth.spec.ts`

  **Commit**: YES
  - Message: `feat(frontend): implement GitHub OAuth authentication`
  - Files: `frontend/src/app/api/auth/`, `frontend/src/lib/auth.ts`, `frontend/src/middleware.ts`

---

- [ ] 20. Implement Infrastructure

  **What to do**:
  - MongoDB connection and repositories
  - Redis client and job queue
  - SSE pub/sub mechanism
  - Docker configuration
  - docker-compose for local development

  **Files to create**:
  - `backend/app/database/__init__.py`
  - `backend/app/database/connection.py`
  - `backend/app/database/repositories/__init__.py`
  - `backend/app/database/repositories/user.py`
  - `backend/app/database/repositories/evaluation.py`
  - `backend/app/database/repositories/result.py`
  - `backend/app/services/redis_client.py`
  - `backend/app/jobs/__init__.py`
  - `backend/app/jobs/queue.py`
  - `backend/app/jobs/worker.py`
  - `backend/Dockerfile`
  - `docker-compose.yml`
  - `.env.example`

  **Must NOT do**:
  - Commit real credentials
  - Skip health checks in Docker

  **Parallelizable**: NO (final integration)

  **References**:
  - `docs/DATABASE_SCHEMA.md` - Collection schemas (TODO 2)
  - `docs/SSE_STREAMING.md` - Pub/Sub patterns (TODO 7)
  - `docs/DEPLOYMENT.md` - Docker config (TODO 13)

  **Acceptance Criteria**:
  - [ ] `docker-compose up` starts all services
  - [ ] MongoDB collections created with indexes
  - [ ] Redis connection verified
  - [ ] Job queue processes evaluation requests
  - [ ] Full E2E test: login → submit → receive results

  **Commit**: YES
  - Message: `feat: implement infrastructure (MongoDB, Redis, Docker)`
  - Files: `backend/app/database/`, `backend/app/jobs/`, `Dockerfile`, `docker-compose.yml`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `docs: add system architecture documentation` | `docs/ARCHITECTURE.md` | Mermaid renders |
| 2 | `docs: add database schema documentation` | `docs/DATABASE_SCHEMA.md` | Schema valid |
| 3 | `docs: add API specification documentation` | `docs/API_SPECIFICATION.md` | OpenAPI valid |
| 4 | `docs: add sommelier agents documentation` | `docs/SOMMELIER_AGENTS.md` | All 6 defined |
| 5 | `docs: add 75 evaluation techniques documentation` | `docs/75_TECHNIQUES.md` | All 75 listed |
| 6 | `docs: add Gemini integration documentation` | `docs/GEMINI_INTEGRATION.md` | Schemas valid |
| 7 | `docs: add SSE streaming documentation` | `docs/SSE_STREAMING.md` | Events defined |
| 8 | `docs: add GitHub integration documentation` | `docs/GITHUB_INTEGRATION.md` | Flow complete |
| 9 | `docs: add frontend components documentation` | `docs/FRONTEND_COMPONENTS.md` | Interfaces valid |
| 10 | `docs: add evaluation pipeline documentation` | `docs/EVALUATION_PIPELINE.md` | Flow complete |
| 11 | `docs: add scoring system documentation` | `docs/SCORING_SYSTEM.md` | House Wine included |
| 12 | `docs: add error handling documentation` | `docs/ERROR_HANDLING.md` | All codes mapped |
| 13 | `docs: add deployment documentation` | `docs/DEPLOYMENT.md` | Vars documented |
| 14 | `docs: add security documentation` | `docs/SECURITY.md` | Mitigations listed |
| 15 | `docs: update README with comprehensive overview` | `README.md` | Links work |
| 16 | `feat(backend): implement 6 sommelier AI agents` | `backend/app/sommeliers/` | Tests pass |
| 17 | `feat(backend): implement core API routes` | `backend/app/api/` | Tests pass |
| 18 | `feat(frontend): implement evaluate, report, history` | `frontend/src/` | E2E pass |
| 19 | `feat(frontend): implement GitHub OAuth authentication` | `frontend/src/` | Auth works |
| 20 | `feat: implement infrastructure (MongoDB, Redis, Docker)` | `backend/`, `docker-compose.yml` | E2E pass |

---

## Success Criteria

### Verification Commands
```bash
# Documentation
find docs -name "*.md" | wc -l  # Expected: 15+

# Backend
cd backend && pytest  # Expected: All tests pass
cd backend && python -c "from app.sommeliers import *"  # Expected: No errors

# Frontend
cd frontend && npm run build  # Expected: Build succeeds
cd frontend && npx playwright test  # Expected: All tests pass

# Infrastructure
docker-compose up -d  # Expected: All services healthy
curl http://localhost:8000/health  # Expected: {"status": "healthy"}
```

### Final Checklist
- [ ] All 15 documentation files present and reviewed
- [ ] All 6 sommeliers implemented with distinct personalities
- [ ] 75 techniques documented with wine mappings
- [ ] House Wine tier (60-69) in scoring system
- [ ] GitHub OAuth working end-to-end
- [ ] SSE streaming delivers real-time progress
- [ ] Docker deployment works locally
- [ ] All tests passing

---

## Timeline

| Week | Dates | Focus | Deliverables |
|------|-------|-------|--------------|
| 1 | Feb 4-10 | Foundation Docs | TODOs 1-4 |
| 2 | Feb 11-17 | Technical Specs | TODOs 5-8 |
| 3 | Feb 18-24 | Implementation Guides | TODOs 9-12 |
| 4 | Feb 25-Mar 3 | Deployment + Backend | TODOs 13-17 |
| 5 | Mar 4-10 | Frontend | TODOs 18-19 |
| 6 | Mar 11-18 | Infrastructure + Testing | TODO 20 + QA |

---

*"Every codebase has terroir. We're here to taste it."* 🍷
