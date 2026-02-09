"""Tests for LLM Grader - LLM-based subjective evaluation.

Tests for the LLMGrader class that evaluates subjective BMAD items.
"""

import pytest


class TestLLMGraderInit:
    def test_llm_grader_initialization(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        assert grader.total_tokens["prompt_tokens"] == 0
        assert grader.total_tokens["completion_tokens"] == 0
        assert grader.total_cost_usd == 0.0

    def test_llm_grader_get_usage_initial(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        usage = grader.get_usage()

        assert usage["prompt_tokens"] == 0
        assert usage["completion_tokens"] == 0
        assert usage["total_tokens"] == 0
        assert usage["cost_usd"] == 0.0


class TestLLMGraderGradeItem:
    @pytest.mark.asyncio
    async def test_grade_item_without_llm_returns_placeholder(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {"readme": "# Test", "file_tree": []}
        result = await grader.grade_item("A1", repo_context, llm=None)

        assert result["item_id"] == "A1"
        assert result["score"] == 0.0
        assert result["max_score"] == 7.0
        assert result["confidence"] == "low"
        assert "LLM grading pending" in result["evidence"][0]
        assert "placeholder" in result["rationale"].lower()

    @pytest.mark.asyncio
    async def test_grade_item_different_items_have_correct_max_scores(self):
        from app.criteria.llm_grader import LLMGrader
        from app.criteria.bmad_items import get_item

        grader = LLMGrader()
        repo_context = {"readme": "", "file_tree": []}

        subjective_items = [
            "A1",
            "A2",
            "A3",
            "A4",
            "B2",
            "B3",
            "B4",
            "C3",
            "C5",
            "D3",
            "D4",
        ]

        for item_id in subjective_items:
            result = await grader.grade_item(item_id, repo_context, llm=None)
            expected_max = get_item(item_id).max_score
            assert result["max_score"] == float(expected_max), (
                f"Wrong max_score for {item_id}"
            )


class TestLLMGraderAssembleContext:
    def test_assemble_context_includes_readme(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {
            "readme": "# Test Project\n\nDescription here",
            "file_tree": ["src/main.py"],
        }
        context = grader._assemble_context(repo_context, max_chars=8000)

        assert "Test Project" in context
        assert "README" in context
        assert "FILE STRUCTURE" in context

    def test_assemble_context_respects_max_chars(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {
            "readme": "# Test\n" + "x" * 10000,
            "file_tree": ["file" + str(i) for i in range(200)],
        }
        context = grader._assemble_context(repo_context, max_chars=100)

        assert len(context) <= 103  # Allow for "..." truncation

    def test_assemble_context_truncates_with_ellipsis(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {
            "readme": "# Test\n" + "x" * 10000,
            "file_tree": [],
        }
        context = grader._assemble_context(repo_context, max_chars=500)

        assert context.endswith("...")

    def test_assemble_context_includes_code_snippets(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {
            "readme": "# Test",
            "file_tree": ["src/main.py"],
            "main_files": [
                {"path": "src/main.py", "content": "def hello():\n    pass"}
            ],
        }
        context = grader._assemble_context(repo_context, max_chars=8000)

        assert "CODE SNIPPETS" in context
        assert "src/main.py" in context
        assert "def hello()" in context

    def test_assemble_context_includes_metadata(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {
            "readme": "# Test",
            "file_tree": [],
            "metadata": {"language": "Python", "stars": 100},
        }
        context = grader._assemble_context(repo_context, max_chars=8000)

        assert "METADATA" in context
        assert "Python" in context


class TestLLMGraderValidateResponse:
    def test_validate_response_valid_response(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        response = {
            "parsed": {
                "score": 5,
                "confidence": "high",
                "evidence": ["Evidence 1", "Evidence 2"],
                "rationale": "Good rationale",
            }
        }

        assert grader._validate_response(response, "A1", 7) is True

    def test_validate_response_missing_required_fields(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        base_response = {
            "parsed": {
                "score": 5,
                "confidence": "high",
                "evidence": ["Evidence"],
                "rationale": "Good",
            }
        }

        for field in ["score", "confidence", "evidence", "rationale"]:
            invalid_response = {
                "parsed": {
                    k: v for k, v in base_response["parsed"].items() if k != field
                }
            }
            assert grader._validate_response(invalid_response, "A1", 7) is False

    def test_validate_response_score_out_of_range(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()

        negative_response = {
            "parsed": {
                "score": -1,
                "confidence": "high",
                "evidence": ["Evidence"],
                "rationale": "Good",
            }
        }
        assert grader._validate_response(negative_response, "A1", 7) is False

        too_high_response = {
            "parsed": {
                "score": 8,
                "confidence": "high",
                "evidence": ["Evidence"],
                "rationale": "Good",
            }
        }
        assert grader._validate_response(too_high_response, "A1", 7) is False

    def test_validate_response_invalid_confidence(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        response = {
            "parsed": {
                "score": 5,
                "confidence": "invalid",
                "evidence": ["Evidence"],
                "rationale": "Good",
            }
        }

        assert grader._validate_response(response, "A1", 7) is False

    def test_validate_response_evidence_not_list(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        response = {
            "parsed": {
                "score": 5,
                "confidence": "high",
                "evidence": "not a list",
                "rationale": "Good",
            }
        }

        assert grader._validate_response(response, "A1", 7) is False

    def test_validate_response_rationale_not_string(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        response = {
            "parsed": {
                "score": 5,
                "confidence": "high",
                "evidence": ["Evidence"],
                "rationale": 123,
            }
        }

        assert grader._validate_response(response, "A1", 7) is False

    def test_validate_response_score_not_numeric(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        response = {
            "parsed": {
                "score": "five",
                "confidence": "high",
                "evidence": ["Evidence"],
                "rationale": "Good",
            }
        }

        assert grader._validate_response(response, "A1", 7) is False


class TestLLMGraderUsage:
    def test_update_usage_increments_tokens(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        grader._update_usage({"input_tokens": 100, "output_tokens": 50})

        usage = grader.get_usage()
        assert usage["prompt_tokens"] == 100
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 150
        assert usage["cost_usd"] > 0

    def test_update_usage_with_alternative_field_names(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        grader._update_usage({"prompt_tokens": 200, "completion_tokens": 100})

        usage = grader.get_usage()
        assert usage["prompt_tokens"] == 200
        assert usage["completion_tokens"] == 100

    def test_get_usage_returns_accumulated_totals(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        grader._update_usage({"input_tokens": 100, "output_tokens": 50})
        grader._update_usage({"input_tokens": 200, "output_tokens": 100})

        usage = grader.get_usage()
        assert usage["prompt_tokens"] == 300
        assert usage["completion_tokens"] == 150
        assert usage["total_tokens"] == 450

    def test_reset_usage_clears_totals(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        grader._update_usage({"input_tokens": 100, "output_tokens": 50})
        grader.reset_usage()

        usage = grader.get_usage()
        assert usage["prompt_tokens"] == 0
        assert usage["completion_tokens"] == 0
        assert usage["total_tokens"] == 0
        assert usage["cost_usd"] == 0.0

    def test_cost_calculation(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        grader._update_usage({"input_tokens": 1000, "output_tokens": 500})

        usage = grader.get_usage()
        expected_cost = (1000 * 0.00003) + (500 * 0.00006)
        assert abs(usage["cost_usd"] - expected_cost) < 0.000001


class TestLLMGraderIntegration:
    @pytest.mark.asyncio
    async def test_grade_item_updates_usage(self):
        from app.criteria.llm_grader import LLMGrader

        grader = LLMGrader()
        repo_context = {"readme": "# Test", "file_tree": []}
        await grader.grade_item("A1", repo_context, llm=None)

        usage = grader.get_usage()
        assert usage == {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
        }
