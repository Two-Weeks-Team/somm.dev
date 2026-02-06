"""Tests for app/graph/state.py - EvaluationState TypedDict"""

from app.graph.state import EvaluationState


class TestEvaluationState:
    """Test cases for EvaluationState TypedDict"""

    def test_evaluation_state_basic_fields(self):
        """Test that EvaluationState has all required input fields"""
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": [], "structure": "monorepo"},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "marcel_result": None,
            "isabella_result": None,
            "heinrich_result": None,
            "sofia_result": None,
            "laurent_result": None,
            "jeanpierre_result": None,
            "completed_sommeliers": [],
            "errors": [],
            "started_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        assert state["repo_url"] == "https://github.com/example/repo"
        assert state["evaluation_criteria"] == "basic"
        assert state["user_id"] == "user123"

    def test_evaluation_state_with_sommelier_results(self):
        """Test EvaluationState with sommelier results populated"""
        sommelier_result = {
            "score": 85,
            "notes": "A robust vintage with excellent structure",
            "confidence": 0.9,
            "techniques_used": ["static_analysis", "metric_extraction"],
            "aspects": {"readability": 8.5, "maintainability": 8.0},
        }
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": ["main.py"], "structure": "simple"},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "marcel_result": sommelier_result,
            "isabella_result": sommelier_result,
            "heinrich_result": sommelier_result,
            "sofia_result": sommelier_result,
            "laurent_result": sommelier_result,
            "jeanpierre_result": None,
            "completed_sommeliers": [],
            "errors": [],
            "started_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        assert state["marcel_result"]["score"] == 85
        assert (
            state["isabella_result"]["notes"]
            == "A robust vintage with excellent structure"
        )

    def test_evaluation_state_progress_tracking(self):
        """Test that progress tracking fields work correctly"""
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": [], "structure": "monorepo"},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "marcel_result": None,
            "isabella_result": None,
            "heinrich_result": None,
            "sofia_result": None,
            "laurent_result": None,
            "jeanpierre_result": None,
            "completed_sommeliers": ["marcel", "isabella"],
            "errors": [],
            "started_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        assert len(state["completed_sommeliers"]) == 2
        assert "marcel" in state["completed_sommeliers"]
        assert "isabella" in state["completed_sommeliers"]

    def test_evaluation_state_error_tracking(self):
        """Test that error tracking works correctly"""
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": [], "structure": "monorepo"},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "marcel_result": None,
            "isabella_result": None,
            "heinrich_result": None,
            "sofia_result": None,
            "laurent_result": None,
            "jeanpierre_result": None,
            "completed_sommeliers": [],
            "errors": ["marcel evaluation failed: API timeout"],
            "started_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        assert len(state["errors"]) == 1
        assert "API timeout" in state["errors"][0]

    def test_evaluation_state_completed_at(self):
        """Test that completed_at field works correctly"""
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": [], "structure": "monorepo"},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "marcel_result": None,
            "isabella_result": None,
            "heinrich_result": None,
            "sofia_result": None,
            "laurent_result": None,
            "jeanpierre_result": None,
            "completed_sommeliers": [],
            "errors": [],
            "started_at": "2024-01-01T00:00:00",
            "completed_at": "2024-01-01T00:05:00",
        }
        assert state["completed_at"] == "2024-01-01T00:05:00"


class TestEvaluationStateTypeHints:
    """Test that EvaluationState has correct type hints"""

    def test_is_typeddict(self):
        """Verify EvaluationState is a TypedDict"""
        from typing import get_type_hints

        assert issubclass(EvaluationState, dict)
        type_hints = get_type_hints(EvaluationState)
        assert "repo_url" in type_hints
        assert "completed_sommeliers" in type_hints
        assert "errors" in type_hints

    def test_list_annotations(self):
        """Test that list fields have correct annotation types"""
        from typing import Annotated, get_origin, get_args, NotRequired

        annotations = getattr(EvaluationState, "__annotations__", {})
        completed_sommeliers_annotation = annotations.get("completed_sommeliers")
        errors_annotation = annotations.get("errors")

        assert get_origin(completed_sommeliers_annotation) is NotRequired
        assert get_origin(errors_annotation) is NotRequired

        completed_inner = get_args(completed_sommeliers_annotation)[0]
        errors_inner = get_args(errors_annotation)[0]

        assert get_origin(completed_inner) is Annotated
        assert get_origin(errors_inner) is Annotated

    def test_rag_context_field_exists(self):
        """Test that rag_context field is defined in EvaluationState"""
        from typing import get_type_hints

        type_hints = get_type_hints(EvaluationState)
        assert "rag_context" in type_hints

    def test_rag_context_accepts_dict(self):
        """Test that EvaluationState accepts rag_context with dict value"""
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": []},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "rag_context": {
                "query": "Evaluate repository",
                "chunks": [{"text": "content", "source": "readme"}],
                "error": None,
            },
        }
        assert state["rag_context"]["query"] == "Evaluate repository"
        assert len(state["rag_context"]["chunks"]) == 1

    def test_rag_context_optional(self):
        """Test that rag_context is optional (NotRequired)"""
        state: EvaluationState = {
            "repo_url": "https://github.com/example/repo",
            "repo_context": {"files": []},
            "evaluation_criteria": "basic",
            "user_id": "user123",
        }
        assert "rag_context" not in state
