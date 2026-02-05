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

### Out of Scope (for this plan)
- Frontend redesign
- New user-facing features unrelated to evaluation quality
- Production infrastructure migration

## Phased Plan (Epic Issues)

### Phase 0: Baseline Alignment & Documentation
- Create ADR directory and ADR-001 for evaluation design alignment
- Document fairthon deltas and adoption decisions
- Add plan execution checklist

**Tests (incl. failure-case)**
- Doc lint: ensure ADR index and plan references exist
- Failure-case: ADR missing required sections triggers CI check

### Phase 1: State & Observability
- Add reducers for parallel state merges
- Add token/cost aggregation in state
- Add evaluation trace metadata in state

**Tests (incl. failure-case)**
- Unit: reducer merge correctness
- Failure-case: missing token metadata does not crash aggregation

### Phase 2: YAML Techniques & Criteria Filters
- Define technique schema (YAML) + loader/validator
- Map techniques to criteria modes and sources (github/pdf/both)
- Add runtime filtering by available inputs

**Tests (incl. failure-case)**
- Unit: YAML schema validation
- Failure-case: invalid YAML → explicit error with fallback

### Phase 3: Multi-Model & BYOK Support
- Provider abstraction (Gemini/Claude/OpenAI)
- Configurable model/temperature per node
- User key injection (BYOK) with safe validation

**Tests (incl. failure-case)**
- Unit: provider selection logic
- Failure-case: invalid key → structured error + safe fallback

### Phase 4: RAG Enrichment
- Retrieval node for repo context enrichment
- Store/reuse retrieval artifacts
- Ensure RAG is optional and guarded

**Tests (incl. failure-case)**
- Unit: retrieval pipeline output shape
- Failure-case: retriever unavailable → graph continues without RAG

### Phase 5: QA & Trajectory Tests
- Trajectory-based test suite for graph flow
- Negative tests: timeouts, LLM errors, missing inputs
- End-to-end smoke with mock providers

**Tests (incl. failure-case)**
- Integration: graph trajectory assertions
- Failure-case: simulated provider timeout recovers with retry policy

## Risks
- Increased config complexity (mitigate with typed schema + validation)
- Provider API variance (mitigate via adapter layer + integration tests)
- RAG cost/latency (mitigate via caching and optional toggles)

## Deliverables
- Plan issues with labels and checklists
- ADRs and updated docs
- Phased implementation with tests and failure-path coverage
