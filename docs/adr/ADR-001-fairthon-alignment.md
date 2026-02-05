# ADR-001: Fairthon Alignment Baseline

## Context
We need a documented baseline for aligning somm.dev with fairthon patterns and
LangGraph best practices while preserving somm.dev domain scope.

## Decision
Adopt the phased alignment plan in `docs/FAIRTHON_ALIGNMENT_PLAN.md` and track
decisions in this ADR series. Phase order is 0 through 5, with Phase 0 as the
mandatory prerequisite.

## Alternatives
- Ad-hoc refactors without a plan (rejected: inconsistent outcomes)
- Full rewrite (rejected: high risk and unnecessary scope)

## Consequences
- Requires ADR maintenance for future changes
- Enables consistent review of scope and dependencies

## Links
- docs/FAIRTHON_ALIGNMENT_PLAN.md
- Issue #67
