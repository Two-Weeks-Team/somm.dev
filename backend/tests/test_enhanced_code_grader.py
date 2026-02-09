"""Tests for Enhanced Code Grader Agent - 17 BMAD items.

Tests for the expanded CodeGraderAgent with full 17-item support.
"""

import pytest


class TestEvaluableItemsExpansion:
    def test_evaluable_items_has_17_items(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        items = agent.get_evaluable_items()
        assert len(items) == 17

    def test_evaluable_items_contains_all_categories(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        items = agent.get_evaluable_items()

        category_a = ["A1", "A2", "A3", "A4"]
        category_b = ["B1", "B2", "B3", "B4"]
        category_c = ["C1", "C2", "C3", "C4", "C5"]
        category_d = ["D1", "D2", "D3", "D4"]

        for item in category_a:
            assert item in items, f"Missing {item} from Category A"
        for item in category_b:
            assert item in items, f"Missing {item} from Category B"
        for item in category_c:
            assert item in items, f"Missing {item} from Category C"
        for item in category_d:
            assert item in items, f"Missing {item} from Category D"


class TestObjectiveItems:
    def test_objective_items_defined(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        objective_items = agent.get_objective_items()
        assert len(objective_items) >= 5
        assert "C1" in objective_items
        assert "C2" in objective_items
        assert "C4" in objective_items
        assert "B1" in objective_items
        assert "B2" in objective_items
        assert "D1" in objective_items
        assert "D2" in objective_items


class TestSubjectiveItems:
    def test_subjective_items_defined(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        subjective_items = agent.get_subjective_items()
        assert "A1" in subjective_items
        assert "A2" in subjective_items
        assert "A3" in subjective_items
        assert "A4" in subjective_items
        assert "B3" in subjective_items
        assert "B4" in subjective_items
        assert "C3" in subjective_items
        assert "C5" in subjective_items
        assert "D3" in subjective_items
        assert "D4" in subjective_items
        assert "B2" not in subjective_items


class TestEvaluateAll:
    @pytest.mark.asyncio
    async def test_evaluate_all_returns_all_17_items(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test Project\n\n## Installation\n\n## Usage\n",
                "file_tree": ["src/main.py", "tests/test_main.py", "package.json"],
                "main_files": [{"path": "main.py", "content": "# test\nprint(1)"}],
                "metadata": {"language": "Python"},
            }
        }
        result = await agent.evaluate_all(context, llm=None)

        assert "item_scores" in result
        assert "_usage" in result

        item_scores = result["item_scores"]
        for item in agent.EVALUABLE_ITEMS:
            assert item in item_scores, f"Missing score for {item}"

    @pytest.mark.asyncio
    async def test_evaluate_all_objective_items_without_llm(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test Project",
                "file_tree": ["src/main.py", "package.json"],
                "main_files": [{"path": "main.py", "content": "print(1)"}],
            }
        }
        result = await agent.evaluate_all(context, llm=None)

        for item in agent.OBJECTIVE_ITEMS:
            assert item in result["item_scores"]
            assert result["item_scores"][item]["confidence"] == "high"

    @pytest.mark.asyncio
    async def test_evaluate_all_subjective_items_without_llm(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test Project",
                "file_tree": [],
                "main_files": [],
            }
        }
        result = await agent.evaluate_all(context, llm=None)

        for item in agent.SUBJECTIVE_ITEMS:
            assert item in result["item_scores"]
            if item in agent.OBJECTIVE_ITEMS:
                assert result["item_scores"][item]["confidence"] == "high"
            else:
                assert result["item_scores"][item]["confidence"] == "low"
                assert (
                    "LLM grading pending" in result["item_scores"][item]["evidence"][0]
                )

    @pytest.mark.asyncio
    async def test_evaluate_all_scores_within_valid_range(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test Project\n\n## Installation\n\n## Usage\n\n## Architecture",
                "file_tree": [
                    "src/main.py",
                    "tests/test_main.py",
                    "package.json",
                    "tsconfig.json",
                    ".eslintrc",
                ],
                "main_files": [{"path": "main.py", "content": "# test\nprint(1)"}],
                "metadata": {"language": "Python"},
            }
        }
        result = await agent.evaluate_all(context, llm=None)

        for item_id, score_data in result["item_scores"].items():
            score = score_data["score"]
            max_score = score_data["max_score"]

            assert score >= 0, f"{item_id} score should be >= 0"
            assert score <= max_score, (
                f"{item_id} score {score} exceeds max {max_score}"
            )

    @pytest.mark.asyncio
    async def test_evaluate_all_empty_context(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {}}
        result = await agent.evaluate_all(context, llm=None)

        assert result["item_scores"] == {}
        assert result["_usage"]["cost_usd"] == 0

    @pytest.mark.asyncio
    async def test_evaluate_all_no_repo_context(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {}
        result = await agent.evaluate_all(context, llm=None)

        assert result["item_scores"] == {}


class TestBackwardCompatibility:
    def test_evaluate_returns_original_5_items(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test",
                "file_tree": [],
                "main_files": [],
            }
        }
        result = agent.evaluate(context)

        original_items = ["D1", "D2", "C4", "B1", "B2"]
        for item in original_items:
            assert item in result["item_scores"], (
                f"Missing {item} in backward compatibility"
            )

    def test_evaluate_schema_unchanged(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test",
                "file_tree": [],
                "main_files": [],
            }
        }
        result = agent.evaluate(context)

        assert "item_scores" in result
        assert "_usage" in result
        assert result["_usage"]["input_tokens"] == 0
        assert result["_usage"]["output_tokens"] == 0
        assert result["_usage"]["cost_usd"] == 0

        for item_code, score_data in result["item_scores"].items():
            assert "score" in score_data
            assert "max_score" in score_data
            assert "evidence" in score_data
            assert "rationale" in score_data
            assert "metrics" in score_data
            assert "confidence" in score_data


class TestC1CodeQuality:
    def test_c1_detects_linter_configs(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [".eslintrc", "src/main.js"],
                "main_files": [{"path": "main.js", "content": "const x = 1;"}],
            }
        }
        result = agent.evaluate(context)

        assert "C1" not in result["item_scores"]

        import asyncio

        async def test_all():
            all_result = await agent.evaluate_all(context, llm=None)
            assert "C1" in all_result["item_scores"]
            assert all_result["item_scores"]["C1"]["max_score"] == 7

        asyncio.run(test_all())


class TestC2TestingCoverage:
    def test_c2_detects_test_coverage_configs(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["tests/test_main.py", ".coveragerc"],
                "main_files": [],
            }
        }

        import asyncio

        async def test_all():
            all_result = await agent.evaluate_all(context, llm=None)
            assert "C2" in all_result["item_scores"]
            assert all_result["item_scores"]["C2"]["max_score"] == 6

        asyncio.run(test_all())


class TestUsageTracking:
    @pytest.mark.asyncio
    async def test_evaluate_all_tracks_usage(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "# Test",
                "file_tree": [],
                "main_files": [],
            }
        }
        result = await agent.evaluate_all(context, llm=None)

        usage = result["_usage"]
        assert "input_tokens" in usage
        assert "output_tokens" in usage
        assert "duration_ms" in usage
        assert "cost_usd" in usage
