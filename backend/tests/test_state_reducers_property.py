"""Property-based tests for state reducers using Hypothesis.

These tests verify the mathematical properties of reducers:
- Idempotence: merge(a, a) == a
- Commutativity: merge(a, b) == merge(b, a)
- Associativity: merge(merge(a, b), c) == merge(a, merge(b, c))
- Determinism: Same inputs always produce same outputs
"""

import pytest
from hypothesis import given, strategies as st, settings

from app.graph.state import (
    merge_methodology_trace,
    merge_item_scores,
    merge_techniques_used,
    merge_excluded_techniques,
    merge_agent_contributions,
)
from app.models.graph import TraceEvent, ItemScore, ExcludedTechnique, AgentContribution


# Strategies for generating test data
timestamp_strategy = st.sampled_from(
    [
        "2026-02-06T10:30:00Z",
        "2026-02-06T10:30:01Z",
        "2026-02-06T10:30:02Z",
        "2026-02-06T10:30:03Z",
        "2026-02-06T10:30:04Z",
    ]
)

agent_strategy = st.sampled_from(
    ["marcel", "isabella", "heinrich", "sofia", "laurent", "jeanpierre"]
)

technique_strategy = st.sampled_from(
    [
        "static_analysis",
        "metric_extraction",
        "code_quality_check",
        "security_audit",
        "innovation_score",
        "implementation_review",
    ]
)

action_strategy = st.sampled_from(
    ["evaluate", "score", "exclude", "enrich", "synthesize"]
)


trace_event_strategy = st.builds(
    TraceEvent,
    step=st.integers(min_value=0, max_value=100),
    timestamp=timestamp_strategy,
    agent=agent_strategy,
    technique_id=technique_strategy,
    item_id=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
    action=action_strategy,
    score_delta=st.one_of(st.none(), st.floats(min_value=-100, max_value=100)),
    evidence_ref=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
)


item_score_strategy = st.builds(
    ItemScore,
    item_id=st.text(min_size=1, max_size=20),
    score=st.floats(min_value=0, max_value=100),
    evaluated_by=agent_strategy,
    technique_id=technique_strategy,
    timestamp=timestamp_strategy,
    notes=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
)


excluded_technique_strategy = st.builds(
    ExcludedTechnique,
    technique_id=technique_strategy,
    reason=st.sampled_from(["timeout", "error", "not_applicable", "unknown"]),
    excluded_at=st.one_of(st.none(), timestamp_strategy),
    excluded_by=st.one_of(st.none(), agent_strategy),
)


agent_contribution_strategy = st.builds(
    AgentContribution,
    agent=agent_strategy,
    technique_ids=st.lists(technique_strategy, unique=True, max_size=3),
    item_ids=st.lists(st.text(min_size=1, max_size=20), unique=True, max_size=3),
    artifacts=st.fixed_dictionaries({}, optional={}),
)


class TestTechniquesUsedReducer:
    """Property-based tests for merge_techniques_used reducer."""

    @given(
        st.lists(st.text(min_size=1, max_size=20), unique=True),
        st.lists(st.text(min_size=1, max_size=20), unique=True),
    )
    @settings(max_examples=100)
    def test_idempotence(self, current, incoming):
        """merge_techniques_used should be idempotent: merge(a, a) == a."""
        merged = merge_techniques_used(current, incoming)
        merged_again = merge_techniques_used(merged, merged)
        assert merged_again == merged

    @given(
        st.lists(st.text(min_size=1, max_size=20), unique=True),
        st.lists(st.text(min_size=1, max_size=20), unique=True),
    )
    @settings(max_examples=100)
    def test_commutativity(self, left, right):
        """merge_techniques_used should be commutative: merge(a, b) == merge(b, a)."""
        merge_left_right = merge_techniques_used(left, right)
        merge_right_left = merge_techniques_used(right, left)
        assert merge_left_right == merge_right_left

    @given(
        st.lists(st.text(min_size=1, max_size=20), unique=True),
        st.lists(st.text(min_size=1, max_size=20), unique=True),
        st.lists(st.text(min_size=1, max_size=20), unique=True),
    )
    @settings(max_examples=100)
    def test_associativity(self, a, b, c):
        """merge_techniques_used should be associative: merge(merge(a, b), c) == merge(a, merge(b, c))."""
        merge_ab = merge_techniques_used(a, b)
        merge_ab_c = merge_techniques_used(merge_ab, c)

        merge_bc = merge_techniques_used(b, c)
        merge_a_bc = merge_techniques_used(a, merge_bc)

        assert merge_ab_c == merge_a_bc

    @given(
        st.lists(st.text(min_size=1, max_size=20), unique=True),
        st.lists(st.text(min_size=1, max_size=20), unique=True),
    )
    @settings(max_examples=100)
    def test_output_is_sorted(self, current, incoming):
        """Output of merge_techniques_used should always be sorted."""
        merged = merge_techniques_used(current, incoming)
        assert merged == sorted(merged)

    @given(
        st.lists(st.text(min_size=1, max_size=20), unique=True),
        st.lists(st.text(min_size=1, max_size=20), unique=True),
    )
    @settings(max_examples=100)
    def test_output_contains_all_unique_elements(self, current, incoming):
        """Output should contain all unique elements from both inputs."""
        merged = merge_techniques_used(current, incoming)
        expected_set = set(current) | set(incoming)
        assert set(merged) == expected_set


class TestMethodologyTraceReducer:
    """Property-based tests for merge_methodology_trace reducer."""

    @given(
        st.lists(trace_event_strategy, max_size=10),
        st.lists(trace_event_strategy, max_size=10),
    )
    @settings(max_examples=50)
    def test_output_is_sorted_by_step(self, current, incoming):
        """Output should be sorted by step, then timestamp, then agent, then technique_id."""
        merged = merge_methodology_trace(current, incoming)
        for i in range(len(merged) - 1):
            key_i = (
                merged[i].step,
                merged[i].timestamp,
                merged[i].agent,
                merged[i].technique_id,
            )
            key_j = (
                merged[i + 1].step,
                merged[i + 1].timestamp,
                merged[i + 1].agent,
                merged[i + 1].technique_id,
            )
            assert key_i <= key_j

    @given(
        st.lists(trace_event_strategy, max_size=10),
        st.lists(trace_event_strategy, max_size=10),
    )
    @settings(max_examples=50)
    def test_no_duplicates_in_output(self, current, incoming):
        """Output should not contain duplicate events based on the dedup key."""
        merged = merge_methodology_trace(current, incoming)
        seen = set()
        for event in merged:
            key = (
                event.step,
                event.agent,
                event.technique_id,
                event.item_id,
                event.action,
            )
            assert key not in seen
            seen.add(key)

    @given(
        st.lists(trace_event_strategy, max_size=10),
        st.lists(trace_event_strategy, max_size=10),
    )
    @settings(max_examples=50)
    def test_determinism(self, current, incoming):
        """Same inputs should always produce same output."""
        merged1 = merge_methodology_trace(current, incoming)
        merged2 = merge_methodology_trace(current, incoming)
        assert merged1 == merged2


class TestItemScoresReducer:
    """Property-based tests for merge_item_scores reducer."""

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20), item_score_strategy, max_size=5
        ),
        st.dictionaries(
            st.text(min_size=1, max_size=20), item_score_strategy, max_size=5
        ),
    )
    @settings(max_examples=50)
    def test_conflict_resolution_latest_wins(self, current, incoming):
        """When the same item_id exists in both inputs, the one with later timestamp should win."""
        merged = merge_item_scores(current, incoming)

        for item_id, score in merged.items():
            if item_id in current and item_id in incoming:
                if incoming[item_id].timestamp > current[item_id].timestamp:
                    assert score == incoming[item_id]
                else:
                    assert score == current[item_id]

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20), item_score_strategy, max_size=5
        ),
        st.dictionaries(
            st.text(min_size=1, max_size=20), item_score_strategy, max_size=5
        ),
    )
    @settings(max_examples=50)
    def test_determinism(self, current, incoming):
        """Same inputs should always produce same output."""
        merged1 = merge_item_scores(current, incoming)
        merged2 = merge_item_scores(current, incoming)
        assert merged1 == merged2

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20), item_score_strategy, max_size=5
        ),
        st.dictionaries(
            st.text(min_size=1, max_size=20), item_score_strategy, max_size=5
        ),
    )
    @settings(max_examples=50)
    def test_contains_all_keys(self, current, incoming):
        """Output should contain all keys from both inputs."""
        merged = merge_item_scores(current, incoming)
        expected_keys = set(current.keys()) | set(incoming.keys())
        assert set(merged.keys()) == expected_keys


class TestExcludedTechniquesReducer:
    """Property-based tests for merge_excluded_techniques reducer."""

    @given(
        st.lists(excluded_technique_strategy, max_size=10),
        st.lists(excluded_technique_strategy, max_size=10),
    )
    @settings(max_examples=50)
    def test_deduplication_by_technique_id(self, current, incoming):
        """Output should have unique technique_ids, with later entries overwriting earlier ones."""
        merged = merge_excluded_techniques(current, incoming)

        technique_ids = [t.technique_id for t in merged]
        assert len(technique_ids) == len(set(technique_ids))

    @given(
        st.lists(excluded_technique_strategy, max_size=10),
        st.lists(excluded_technique_strategy, max_size=10),
    )
    @settings(max_examples=50)
    def test_determinism(self, current, incoming):
        """Same inputs should always produce same output."""
        merged1 = merge_excluded_techniques(current, incoming)
        merged2 = merge_excluded_techniques(current, incoming)

        assert merged1 == merged2


class TestAgentContributionsReducer:
    """Property-based tests for merge_agent_contributions reducer."""

    @given(
        st.dictionaries(agent_strategy, agent_contribution_strategy, max_size=3),
        st.dictionaries(agent_strategy, agent_contribution_strategy, max_size=3),
    )
    @settings(max_examples=50)
    def test_technique_ids_union(self, current, incoming):
        """Merged contributions should contain union of technique_ids for each agent."""
        merged = merge_agent_contributions(current, incoming)

        for agent, contribution in merged.items():
            current_techniques = set(
                current.get(agent, AgentContribution(agent=agent)).technique_ids
            )
            incoming_techniques = set(
                incoming.get(agent, AgentContribution(agent=agent)).technique_ids
            )
            expected_union = current_techniques | incoming_techniques
            assert set(contribution.technique_ids) == expected_union

    @given(
        st.dictionaries(agent_strategy, agent_contribution_strategy, max_size=3),
        st.dictionaries(agent_strategy, agent_contribution_strategy, max_size=3),
    )
    @settings(max_examples=50)
    def test_determinism(self, current, incoming):
        """Same inputs should always produce same output."""
        merged1 = merge_agent_contributions(current, incoming)
        merged2 = merge_agent_contributions(current, incoming)
        assert merged1 == merged2

    @given(
        st.dictionaries(agent_strategy, agent_contribution_strategy, max_size=3),
        st.dictionaries(agent_strategy, agent_contribution_strategy, max_size=3),
    )
    @settings(max_examples=50)
    def test_contains_all_agents(self, current, incoming):
        """Output should contain all agents from both inputs."""
        merged = merge_agent_contributions(current, incoming)
        expected_agents = set(current.keys()) | set(incoming.keys())
        assert set(merged.keys()) == expected_agents
