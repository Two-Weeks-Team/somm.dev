"""Tests for Code Grader Agent - Deterministic evaluation without LLM.

Phase 2.1: Code Grader Base Module
RED Phase - These tests define the expected behavior.
"""

import pytest
from dataclasses import dataclass
from typing import Any


class TestCodeGraderImports:
    def test_import_code_grader_module(self):
        from app.agents import code_grader

        assert code_grader is not None

    def test_import_code_grader_result(self):
        from app.agents.code_grader import CodeGraderResult

        assert CodeGraderResult is not None

    def test_import_code_grader_agent(self):
        from app.agents.code_grader import CodeGraderAgent

        assert CodeGraderAgent is not None


class TestCodeGraderResult:
    def test_result_is_dataclass(self):
        from app.agents.code_grader import CodeGraderResult

        result = CodeGraderResult(
            item_code="D1",
            score=3.0,
            max_score=6.0,
            evidence=["README exists"],
            rationale="Basic README present",
            metrics={"readme_exists": True},
        )
        assert result.item_code == "D1"
        assert result.score == 3.0
        assert result.max_score == 6.0

    def test_result_evidence_is_list(self):
        from app.agents.code_grader import CodeGraderResult

        result = CodeGraderResult(
            item_code="D1",
            score=1.0,
            max_score=6.0,
            evidence=["Point 1", "Point 2"],
            rationale="Test",
            metrics={},
        )
        assert isinstance(result.evidence, list)
        assert len(result.evidence) == 2


class TestCodeGraderAgentBasics:
    def test_agent_instantiation(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        assert agent is not None
        assert agent.name == "Code Grader"

    def test_agent_get_evaluable_items(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        items = agent.get_evaluable_items()
        assert "D1" in items
        assert "D2" in items
        assert "C4" in items
        assert "B1" in items
        assert "B2" in items

    def test_agent_evaluate_returns_dict(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "# Test", "file_tree": []}}
        result = agent.evaluate(context)
        assert isinstance(result, dict)
        assert "item_scores" in result
        assert "_usage" in result

    def test_agent_usage_is_zero_cost(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "# Test", "file_tree": []}}
        result = agent.evaluate(context)
        usage = result["_usage"]
        assert usage["input_tokens"] == 0
        assert usage["output_tokens"] == 0
        assert usage["cost_usd"] == 0


class TestD1ReadmeQuality:
    def test_d1_no_readme_score_zero(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": []}}
        result = agent.evaluate(context)
        assert "D1" in result["item_scores"]
        assert result["item_scores"]["D1"]["score"] == 0

    def test_d1_readme_exists_gets_point(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "# My Project", "file_tree": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["D1"]["score"] >= 1

    def test_d1_long_readme_gets_more_points(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        long_readme = "# Project\n" + "Content " * 500
        context = {"repo_context": {"readme": long_readme, "file_tree": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["D1"]["score"] >= 2

    def test_d1_readme_with_installation_section(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        readme = "# Project\n\n## Installation\n\nRun `npm install`"
        context = {"repo_context": {"readme": readme, "file_tree": []}}
        result = agent.evaluate(context)
        metrics = result["item_scores"]["D1"]["metrics"]
        assert metrics["has_installation"] is True

    def test_d1_readme_with_usage_section(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        readme = "# Project\n\n## Usage\n\nHow to use this"
        context = {"repo_context": {"readme": readme, "file_tree": []}}
        result = agent.evaluate(context)
        metrics = result["item_scores"]["D1"]["metrics"]
        assert metrics["has_usage"] is True

    def test_d1_max_score_is_six(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "# Test", "file_tree": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["D1"]["max_score"] == 6


class TestC4TestExistence:
    def test_c4_no_tests_score_zero(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": ["main.py", "app.py"]}}
        result = agent.evaluate(context)
        assert "C4" in result["item_scores"]
        assert result["item_scores"]["C4"]["score"] == 0

    def test_c4_test_folder_gets_point(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["main.py", "tests/test_main.py"],
            }
        }
        result = agent.evaluate(context)
        assert result["item_scores"]["C4"]["score"] >= 1

    def test_c4_ci_config_gets_point(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["main.py", ".github/workflows/ci.yml"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["C4"]["metrics"]
        assert metrics["has_ci"] is True

    def test_c4_multiple_test_files(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [
                    "main.py",
                    "tests/test_a.py",
                    "tests/test_b.py",
                    "tests/test_c.py",
                ],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["C4"]["metrics"]
        assert metrics["test_file_count"] >= 3

    def test_c4_max_score_is_four(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["C4"]["max_score"] == 4


class TestB2SystemArchitecture:
    def test_b2_no_structure_score_zero(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": []}}
        result = agent.evaluate(context)
        assert "B2" in result["item_scores"]
        assert result["item_scores"]["B2"]["score"] == 0

    def test_b2_organized_folders_get_point(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["src/main.py", "src/utils.py"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B2"]["metrics"]
        assert metrics["folder_organization"] is True

    def test_b2_modular_structure_gets_point(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [
                    "src/components/Button.tsx",
                    "src/services/api.ts",
                    "src/utils/helpers.ts",
                ],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B2"]["metrics"]
        assert metrics["modular_structure"] is True

    def test_b2_static_analysis_config(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["main.py", "pyproject.toml", "ruff.toml"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B2"]["metrics"]
        assert len(metrics["static_analysis_tools"]) > 0

    def test_b2_max_score_is_six(self):
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["B2"]["max_score"] == 6
