# Fairthon Alignment & LangGraph Best Practices Plan

## Goal
Align somm.dev with fairthon's proven architecture patterns and LangGraph best practices while preserving somm.dev domain concept and UX. Deliver a phased plan to reach parity on robustness, extensibility, and observability.

## Reference Inputs
- Fairthon repo: https://github.com/Two-Weeks-Team/fairthon (private)
- LangGraph official docs (best practices, state, testing, deployment)
- somm.dev current architecture: docs/ARCHITECTURE.md, docs/EVALUATION_PIPELINE.md

## Current State Summary (somm.dev)
- LangGraph fan-out/fan-in graph with 6 nodes and MongoDB checkpointer
- Deterministic evaluators: CodeGrader + CodebaseAnalyzer already present
- Single-provider LLM (Gemini) with fixed prompts
- Basic state schema without advanced reducers or cost tracking

## Fairthon Patterns Worth Mirroring
- TypedDict with `total=False` and explicit reducers for parallel merges
- Rich state tracking: tokens, cost, trace, methodology steps
- YAML-based techniques/templates for non-code extensibility
- Multi-model provider support + BYOK + model selection
- RAG enrichment nodes and source-conditional techniques
- ADRs and doc structure for decision tracking
- **Graph visualization API with ReactFlow + 3D support**
- **Multiple evaluation modes (Six Hats, Full Techniques)**

## LangGraph Best Practice Alignment Targets
- Minimal, well-typed state with reducers for parallel merges
- Node granularity: isolate I/O and LLM calls, explicit retries
- Observability: cost/token aggregation and trace logging
- Testing: node isolation tests, trajectory tests, and negative cases
- Checkpointer choice: keep MongoDB for now, document constraints

## Scope
### In Scope
- State/reducer upgrades, token/cost tracking
- YAML technique registry + criteria/filters
- Multi-model provider abstraction (Gemini/Claude/GPT)
- RAG enrichment + retrieval strategy
- ADR + documentation updates
- Phased issues with explicit tests (including failure-path tests)
- **Graph visualization API (ReactFlow + 3D)**
- **Two evaluation modes: Six Hats (6) + Full Techniques (75)**
- **Methodology trace + item-level scoring**
- **Graph caching in MongoDB**

### Out of Scope (for this plan)
- Frontend redesign
- New user-facing features unrelated to evaluation quality
- Production infrastructure migration
- bmad_quick mode (Fairthon's third mode)

---

## Phased Plan (Epic Issues)

### Phase 0: Baseline Alignment & Documentation
- Create ADR directory and ADR-001 for evaluation design alignment
- Document fairthon deltas and adoption decisions
- Add plan execution checklist

**Tests (incl. failure-case)**
- Doc lint: ensure ADR index and plan references exist
- Failure-case: ADR missing required sections triggers CI check

---

### Phase 1: State & Observability
- Add reducers for parallel state merges
- Add token/cost aggregation in state
- Add evaluation trace metadata in state

**Tests (incl. failure-case)**
- Unit: reducer merge correctness
- Failure-case: missing token metadata does not crash aggregation

---

### Phase G0: Graph Contracts & Mode Registry
> **NEW: Graph Track - Contracts and Schemas**

Define stable API contracts for graph visualization before implementation.

**Tasks**
- Define Pydantic response models:
  - `ReactFlowGraph`: `nodes[]`, `edges[]`, `viewport?`, `meta`
  - `Graph3DPayload`: `nodes[]` (with `position3d`), `edges[]` (with `bundled_path?`), `steps[]`, `metadata`
- Define evaluation mode enum:
  - `six_hats` (6 parallel agents)
  - `full_techniques` (75 techniques comprehensive analysis)
- Document graph schema versioning strategy

**Deliverables**
- ADR-002: Graph Visualization Contracts
- Pydantic models in `backend/app/models/graph.py`

**Dependencies**: None

**Tests**
- Model validation tests with golden JSON fixtures
- Schema version compatibility tests

**Effort**: Small

---

### Phase G1: Enhanced State - Methodology Trace & Item-Level Scoring
> **NEW: Graph Track - State Enhancements**

Create Fairthon-like "Agent -> Technique -> Item" traceability for rich visualization.

**Tasks**
- Extend `backend/app/graph/state.py` with:
  ```python
  # Methodology trace (ordered evaluation steps)
  methodology_trace: Annotated[list[dict], merge_methodology_trace]
  
  # Item-level scores with merge reducer
  item_scores: Annotated[dict[str, ItemScore], merge_item_scores]
  
  # Techniques tracking
  techniques_used: Annotated[list[str], merge_techniques_used]
  excluded_techniques: Annotated[list[dict], merge_excluded_techniques]
  
  # Agent contributions
  agent_contributions: Annotated[dict[str, list], merge_agent_contributions]
  
  # Normalized scoring
  raw_score: float | None
  max_possible: float | None
  normalized_score: float | None
  evaluated_count: int | None
  unevaluated_count: int | None
  coverage_rate: float | None
  ```
- Define trace event schema:
  ```python
  TraceEvent = {
      "step": int,
      "timestamp": str,
      "agent": str,  # sommelier name
      "technique_id": str,
      "item_id": str | None,
      "action": str,
      "score_delta": float | None,
      "evidence_ref": str | None
  }
  ```
- Update sommelier nodes to emit technique/item results
- Update synthesis node to compute normalized scores

**Deliverables**
- Updated state definition with all reducers
- Trace schema documentation

**Dependencies**: Phase 1 (basic reducers)

**Tests**
- Unit: reducer associativity and commutativity
- Unit: trace ordering by step number
- Unit: normalization excludes unevaluated items
- Failure-case: missing fields don't crash merges

**Effort**: Large

---

### Phase 2: YAML Techniques & Criteria Filters
- Define technique schema (YAML) + loader/validator
- Map techniques to criteria modes and sources (github/pdf/both)
- Add runtime filtering by available inputs

**Tests (incl. failure-case)**
- Unit: YAML schema validation
- Failure-case: invalid YAML -> explicit error with fallback

---

### Phase G2: Graph Visualization API v1 - Topology & Execution
> **NEW: Graph Track - API Endpoints**

Implement ReactFlow-compatible graph endpoints.

**Tasks**
- Add new router: `backend/app/api/routes/graph.py`
- Implement endpoints:
  - `GET /api/evaluate/{id}/graph` -> ReactFlow JSON (topology)
  - `GET /api/evaluate/{id}/graph/timeline` -> execution events
  - `GET /api/evaluate/{id}/graph/mode` -> current evaluation mode
- ReactFlow node mapping:
  - Six Hats mode: `__start__` -> `rag_enrich?` -> 6 sommeliers (parallel) -> `jeanpierre` -> `__end__`
  - Full Techniques mode: Extended topology with technique groups
- Node overlay data: `status`, `progress`, `token_usage`, `cost`, `timestamps`
- Authorization: reuse ownership checks from evaluate routes

**Deliverables**
- Working `/api/evaluate/{id}/graph` endpoint
- OpenAPI documentation

**Dependencies**: Phase G0, Phase G1 (for execution overlay)

**Tests**
- API: non-owner access rejected (401/403)
- API: response validates against Pydantic contract
- Snapshot: topology output stability

**Effort**: Medium

---

### Phase 3: Multi-Model & BYOK Support
- Provider abstraction (Gemini/Claude/OpenAI)
- Configurable model/temperature per node
- User key injection (BYOK) with safe validation

**Tests (incl. failure-case)**
- Unit: provider selection logic
- Failure-case: invalid key -> structured error + safe fallback

---

### Phase G3: 3D Graph Builder v1 - Layered Layout
> **NEW: Graph Track - 3D Visualization**

Deliver basic 3D visualization with deterministic layout.

**Tasks**
- Implement 3D layout builder:
  - Layered layout: start -> (rag?) -> parallel agents -> synthesis -> end
  - Deterministic positioning (`position3d: {x, y, z}`)
- Add step tracking:
  - Map execution to animation steps from `methodology_trace`
  - Output `steps[]` for frontend animation
- Implement endpoint:
  - `GET /api/evaluate/{id}/graph-3d` -> Graph3DPayload

**Deliverables**
- 3D graph endpoint
- Animation step metadata

**Dependencies**: Phase G2

**Tests**
- Determinism: same input -> same positions
- Bounds: no NaN/inf coordinates
- Step ordering: monotonically increasing

**Effort**: Medium

---

### Phase G4: 3D Graph Builder v2 - Technique/Item Layers + Edge Bundling
> **NEW: Graph Track - Advanced 3D Features**

Full Fairthon parity with technique nodes and edge bundling.

**Tasks**
- Expand 3D topology with layers:
  - Agent layer (sommeliers)
  - Technique layer (from YAML techniques)
  - Item layer (from `item_scores`)
  - Synthesis layer
- Implement FDEB edge bundling:
  - Bundle dense edge sets (configurable threshold)
  - Output `bundled_path` polylines
- Excluded technique visualization:
  - Distinct styling metadata for excluded items
- Per-evaluation step numbers for animation

**Deliverables**
- Extended 3D payload with technique/item nodes
- Edge bundling implementation
- Debug metadata (exclusion reasons)

**Dependencies**: Phase G1, Phase G5 (caching for performance)

**Tests**
- Property: each edge produces non-empty path
- Property: endpoints anchored to node positions
- Performance: bundling completes under threshold for typical sizes

**Effort**: Large

---

### Phase G5: Graph Caching in MongoDB
> **NEW: Graph Track - Performance Optimization**

Cache computed graph payloads for performance.

**Tasks**
- Add MongoDB repository: `backend/app/database/repositories/graph_cache.py`
  - Collection: `graph_data`
  - TTL index via `expires_at` or `cached_at`
- Cache key structure:
  - `evaluation_id`
  - `graph_mode` (six_hats | full_techniques)
  - `layout_params_hash`
  - `techniques_version` (hash for invalidation)
- Endpoint behavior:
  - Default: serve cached if present
  - `?refresh=true`: recompute and overwrite
- Stale-while-revalidate (optional): serve stale + background rebuild

**Deliverables**
- Graph cache repository
- TTL index creation on startup
- Cache integration in graph endpoints

**Dependencies**: Phase G2, Phase G3

**Tests**
- Integration: write/read/cache-hit/cache-bypass
- Key stability: same params -> same key

**Effort**: Medium

---

### Phase 4: RAG Enrichment
- Retrieval node for repo context enrichment
- Store/reuse retrieval artifacts
- Ensure RAG is optional and guarded

**Tests (incl. failure-case)**
- Unit: retrieval pipeline output shape
- Failure-case: retriever unavailable -> graph continues without RAG

---

### Phase 5: QA & Trajectory Tests
- Trajectory-based test suite for graph flow
- Negative tests: timeouts, LLM errors, missing inputs
- End-to-end smoke with mock providers

**Tests (incl. failure-case)**
- Integration: graph trajectory assertions
- Failure-case: simulated provider timeout recovers with retry policy

---

### Phase G6: Multiple Evaluation Modes Implementation
> **NEW: Graph Track - Multi-Mode Support**

Implement two distinct evaluation modes with different graph topologies.

**Tasks**
- Implement graph registry:
  ```python
  GRAPH_REGISTRY = {
      "six_hats": create_six_hats_graph,
      "full_techniques": create_full_techniques_graph,
  }
  ```
- **Six Hats Mode (6 agents)**:
  - Topology: `__start__` -> `rag_enrich` -> `prepare` -> [6 parallel hats] -> `blue_synthesis` -> `finalize` -> `rag_store` -> `__end__`
  - Agents: white_hat, red_hat, black_hat, yellow_hat, green_hat, code_grader (parallel)
  - Blue hat synthesizes all results
- **Full Techniques Mode (75 techniques)**:
  - Topology: `__start__` -> `rag_enrich` -> `prepare` -> `baseline` -> [8 technique groups] -> `deep_synthesis` -> `finalize` -> `rag_store` -> `__end__`
  - Groups: analysis, innovation, risk, empathy, feasibility, opportunity, presentation, synthesis
  - 75 individual techniques distributed across groups
- Mode-aware visualization endpoints
- Mode-aware caching keys

**Deliverables**
- Two complete graph definitions
- Mode selection in evaluation API
- Updated visualization for each mode
- Documentation: supported modes and visualization

**Dependencies**: Phase G1, Phase G2, Phase G3

**Tests**
- Trajectory: correct node ordering per mode
- Mode switch: different topologies returned
- Negative: unsupported mode -> structured error

**Effort**: Large

---

## Evaluation Modes Specification

### Six Hats Mode (6)
```
Topology:
START -> rag_enrich -> prepare
                          |
          +-------+-------+-------+-------+-------+
          v       v       v       v       v       v
       white   red    black  yellow  green  code_grader
          |       |       |       |       |       |
          +-------+-------+-------+-------+-------+
                          |
                   blue_synthesis
                          |
                      finalize
                          |
                     rag_store
                          |
                         END

Characteristics:
- 6 parallel evaluation agents
- ~90 seconds typical execution
- Balanced coverage across perspectives
```

### Full Techniques Mode (75)
```
Topology:
START -> rag_enrich -> prepare -> bmad_baseline
                                       |
    +--------+--------+--------+--------+--------+--------+--------+
    v        v        v        v        v        v        v        v
analysis  innov   risk    empathy  feasib  opport  present  synth
    |        |        |        |        |        |        |        |
    +--------+--------+--------+--------+--------+--------+--------+
                                       |
                                deep_synthesis
                                       |
                                   finalize
                                       |
                                  rag_store
                                       |
                                      END

Characteristics:
- 75 individual techniques across 8 groups
- ~3 minutes typical execution
- Comprehensive analysis coverage
```

---

## Risks
- Increased config complexity (mitigate with typed schema + validation)
- Provider API variance (mitigate via adapter layer + integration tests)
- RAG cost/latency (mitigate via caching and optional toggles)
- **Graph caching invalidation complexity (mitigate with version hashing)**
- **3D rendering performance on large graphs (mitigate with LOD and bundling)**

---

## Deliverables
- Plan issues with labels and checklists
- ADRs and updated docs
- Phased implementation with tests and failure-path coverage
- **Graph visualization API (ReactFlow + 3D)**
- **Two evaluation modes with distinct topologies**
- **MongoDB graph caching layer**

---

## Plan Execution Checklist

### Core Alignment
- [ ] Phase 0 completed and merged (ADR baseline)
- [ ] Phase 1 completed and merged (state reducers + observability)
- [ ] Phase 2 completed and merged (YAML techniques + filters)
- [ ] Phase 3 completed and merged (multi-model + BYOK)
- [ ] Phase 4 completed and merged (RAG enrichment)
- [ ] Phase 5 completed and merged (trajectory + failure-path QA)

### Graph Track
- [ ] Phase G0 completed and merged (graph contracts + mode registry)
- [ ] Phase G1 completed and merged (enhanced state + methodology trace)
- [ ] Phase G2 completed and merged (graph visualization API v1)
- [ ] Phase G3 completed and merged (3D graph builder v1)
- [ ] Phase G4 completed and merged (3D v2 + edge bundling)
- [ ] Phase G5 completed and merged (graph caching)
- [ ] Phase G6 completed and merged (multi-mode implementation)

---

## Phase Dependencies Diagram

```
Phase 0 (ADR)
    |
    v
Phase 1 (State) -----> Phase G0 (Contracts)
    |                       |
    v                       v
Phase 2 (YAML) <----- Phase G1 (Enhanced State)
    |                       |
    v                       v
Phase 3 (BYOK)        Phase G2 (Graph API v1)
    |                       |
    v                       v
Phase 4 (RAG)         Phase G3 (3D v1)
    |                       |
    v                       v
Phase 5 (QA)          Phase G5 (Caching) ----> Phase G4 (3D v2)
                            |
                            v
                      Phase G6 (Multi-Mode)
```

---

*Last Updated: 2026-02-06*
*Author: somm.dev Team*
