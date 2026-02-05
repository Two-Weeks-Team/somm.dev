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


class TestD2CodeComments:
    """D2 코드 주석 평가 테스트"""

    def test_d2_no_files_score_zero(self):
        """main_files가 없으면 점수 0"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": [], "main_files": []}}
        result = agent.evaluate(context)
        assert "D2" in result["item_scores"]
        assert result["item_scores"]["D2"]["score"] == 0

    def test_d2_no_comments_low_score(self):
        """주석이 없는 코드는 낮은 점수"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {"path": "main.py", "content": "x = 1\ny = 2\nprint(x + y)"}
                ],
            }
        }
        result = agent.evaluate(context)
        assert result["item_scores"]["D2"]["score"] == 0

    def test_d2_with_comments_gets_point(self):
        """주석이 있으면 점수 획득"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {"path": "main.py", "content": "# This is a comment\nx = 1\ny = 2"}
                ],
            }
        }
        result = agent.evaluate(context)
        assert result["item_scores"]["D2"]["score"] >= 1

    def test_d2_high_comment_ratio_gets_more_points(self):
        """높은 주석 비율은 추가 점수"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        # 5% 이상 주석 비율을 만들기 위해 20줄 중 1줄 이상 주석
        lines = ["# Comment line"] * 5 + ["code = 'value'"] * 15
        content = "\n".join(lines)
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [{"path": "main.py", "content": content}],
            }
        }
        result = agent.evaluate(context)
        assert result["item_scores"]["D2"]["score"] >= 2
        assert result["item_scores"]["D2"]["metrics"]["comment_ratio"] >= 5

    def test_d2_with_docstrings(self):
        """Docstring이 있으면 점수 획득"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {
                        "path": "main.py",
                        "content": '''def hello():
    """This is a docstring."""
    pass
''',
                    }
                ],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["D2"]["metrics"]
        assert metrics["has_docstrings"] is True

    def test_d2_with_type_hints_python(self):
        """Python 타입 힌트가 있으면 점수 획득"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {
                        "path": "main.py",
                        "content": "def greet(name: str) -> str:\n    return f'Hello, {name}'",
                    }
                ],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["D2"]["metrics"]
        assert metrics["has_type_hints"] is True

    def test_d2_with_type_hints_typescript(self):
        """TypeScript 타입이 있으면 점수 획득"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {
                        "path": "main.ts",
                        "content": "const x: string = 'hello';\nconst y: number = 42;",
                    }
                ],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["D2"]["metrics"]
        assert metrics["has_type_hints"] is True

    def test_d2_js_comments(self):
        """JavaScript 스타일 주석 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {
                        "path": "main.js",
                        "content": "// Single line comment\nconst x = 1;\n/* Multi-line */",
                    }
                ],
            }
        }
        result = agent.evaluate(context)
        assert result["item_scores"]["D2"]["score"] >= 1
        assert result["item_scores"]["D2"]["metrics"]["comment_lines"] >= 2

    def test_d2_jsdoc_detected(self):
        """JSDoc 스타일 문서화 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": [],
                "main_files": [
                    {
                        "path": "main.js",
                        "content": """/**
 * @param {string} name - The name
 * @returns {string} Greeting
 */
function greet(name) { return 'Hello ' + name; }
""",
                    }
                ],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["D2"]["metrics"]
        assert metrics["has_docstrings"] is True

    def test_d2_max_score_is_four(self):
        """D2 최대 점수는 4점"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": [], "main_files": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["D2"]["max_score"] == 4


class TestB1TechStack:
    """B1 기술 스택 평가 테스트"""

    def test_b1_no_package_manager_low_score(self):
        """패키지 관리자가 없으면 낮은 점수"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": ["main.py", "app.py"]}}
        result = agent.evaluate(context)
        assert "B1" in result["item_scores"]
        assert result["item_scores"]["B1"]["score"] == 0

    def test_b1_with_package_json(self):
        """package.json이 있으면 npm 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["package.json", "src/index.js"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert "npm" in metrics["dependency_types"]
        assert result["item_scores"]["B1"]["score"] >= 1

    def test_b1_with_requirements_txt(self):
        """requirements.txt가 있으면 pip 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["requirements.txt", "main.py"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert "pip" in metrics["dependency_types"]

    def test_b1_with_pyproject_toml(self):
        """pyproject.toml이 있으면 pip 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["pyproject.toml", "src/main.py"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert "pip" in metrics["dependency_types"]

    def test_b1_with_go_mod(self):
        """go.mod가 있으면 go 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["go.mod", "main.go"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert "go" in metrics["dependency_types"]

    def test_b1_polyglot_project(self):
        """다중 패키지 관리자 사용 시 추가 점수"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["package.json", "requirements.txt", "main.py"],
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert len(metrics["dependency_types"]) >= 2
        # 패키지 관리자 1점 + 폴리글랏 1점 = 2점 이상
        assert result["item_scores"]["B1"]["score"] >= 2

    def test_b1_with_primary_language(self):
        """주요 언어 정보가 있으면 점수 획득"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["main.py"],
                "metadata": {"language": "Python"},
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert metrics["primary_language"] == "Python"
        assert result["item_scores"]["B1"]["score"] >= 1

    def test_b1_with_languages_dict(self):
        """languages dict에서 주요 언어 추출"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["main.py"],
                "languages": {"Python": 80, "JavaScript": 20},
            }
        }
        result = agent.evaluate(context)
        metrics = result["item_scores"]["B1"]["metrics"]
        assert metrics["primary_language"] == "Python"

    def test_b1_modern_framework_next(self):
        """Next.js 프레임워크 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["package.json", "next.config.js", "pages/index.tsx"],
            }
        }
        result = agent.evaluate(context)
        # 패키지 관리자 1점 + 모던 프레임워크 2점 = 3점 이상
        assert result["item_scores"]["B1"]["score"] >= 3

    def test_b1_modern_framework_fastapi(self):
        """FastAPI 프레임워크 감지"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {
            "repo_context": {
                "readme": "",
                "file_tree": ["requirements.txt", "app/fastapi/main.py"],
            }
        }
        result = agent.evaluate(context)
        # 패키지 관리자 1점 + 모던 프레임워크 2점 = 3점 이상
        assert result["item_scores"]["B1"]["score"] >= 3

    def test_b1_max_score_is_seven(self):
        """B1 최대 점수는 7점"""
        from app.agents.code_grader import CodeGraderAgent

        agent = CodeGraderAgent()
        context = {"repo_context": {"readme": "", "file_tree": []}}
        result = agent.evaluate(context)
        assert result["item_scores"]["B1"]["max_score"] == 7


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
