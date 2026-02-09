import re
from dataclasses import dataclass
from typing import Any

from app.criteria.llm_grader import LLMGrader


@dataclass
class CodeGraderResult:
    item_code: str
    score: float
    max_score: float
    evidence: list[str]
    rationale: str
    metrics: dict[str, Any]


class CodeGraderAgent:
    EVALUABLE_ITEMS = [
        "A1",
        "A2",
        "A3",
        "A4",
        "B1",
        "B2",
        "B3",
        "B4",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "D1",
        "D2",
        "D3",
        "D4",
    ]

    OBJECTIVE_ITEMS = ["C1", "C2", "C4", "B1", "B2", "D1", "D2"]

    SUBJECTIVE_ITEMS = [
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

    ORIGINAL_ITEMS = ["D1", "D2", "C4", "B1", "B2"]

    def __init__(self):
        self.name = "Code Grader"
        self.description = "Deterministic code-based evaluation"

    def get_evaluable_items(self) -> list[str]:
        return list(self.EVALUABLE_ITEMS)

    def get_objective_items(self) -> list[str]:
        return list(self.OBJECTIVE_ITEMS)

    def get_subjective_items(self) -> list[str]:
        return list(self.SUBJECTIVE_ITEMS)

    def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate repository using deterministic heuristics.

        Maintains backward compatibility - returns only original 5 items.
        Use evaluate_all() for full 17-item evaluation.
        """
        repo_context = context.get("repo_context", {})

        if not repo_context:
            return {
                "item_scores": {},
                "_usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "duration_ms": 0,
                    "cost_usd": 0,
                },
            }

        item_scores = {}

        evaluation_map = {
            "D1": self._evaluate_readme_quality,
            "D2": self._evaluate_code_comments,
            "C4": self._evaluate_test_existence,
            "B1": self._evaluate_tech_stack,
            "B2": self._evaluate_system_architecture,
        }

        for item_code, method in evaluation_map.items():
            result = method(repo_context)
            if result:
                item_scores[item_code] = self._to_item_score(result)

        return {
            "item_scores": item_scores,
            "_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "duration_ms": 0,
                "cost_usd": 0,
            },
        }

    async def evaluate_all(
        self, context: dict[str, Any], llm: Any = None
    ) -> dict[str, Any]:
        """Evaluate all 17 BMAD items using objective heuristics and optional LLM.

        Args:
            context: Repository context dictionary
            llm: Optional LLM client for subjective items. If None, subjective
                 items return placeholder scores with confidence="low".

        Returns:
            Dictionary with all 17 item scores and usage tracking
        """
        repo_context = context.get("repo_context", {})

        if not repo_context:
            return {
                "item_scores": {},
                "_usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "duration_ms": 0,
                    "cost_usd": 0,
                },
            }

        item_scores = {}

        objective_map = {
            "C1": self._evaluate_code_quality,
            "C2": self._evaluate_testing_coverage,
            "C4": self._evaluate_test_existence,
            "B1": self._evaluate_tech_stack,
            "B2": self._evaluate_system_architecture,
            "D1": self._evaluate_readme_quality,
            "D2": self._evaluate_code_comments,
        }

        for item_code, method in objective_map.items():
            result = method(repo_context)
            if result:
                item_score = self._to_item_score(result)
                item_scores[item_code] = item_score

        llm_grader = LLMGrader()
        for item_code in self.SUBJECTIVE_ITEMS:
            if llm is not None or item_code not in item_scores:
                result = await llm_grader.grade_item(item_code, repo_context, llm)
                item_scores[item_code] = {
                    "item_code": result["item_id"],
                    "score": result["score"],
                    "max_score": result["max_score"],
                    "evidence": result["evidence"],
                    "rationale": result["rationale"],
                    "confidence": result["confidence"],
                    "metrics": {},
                }

        llm_usage = llm_grader.get_usage()
        usage = {
            "input_tokens": llm_usage["prompt_tokens"],
            "output_tokens": llm_usage["completion_tokens"],
            "duration_ms": 0,
            "cost_usd": llm_usage["cost_usd"],
        }

        return {
            "item_scores": item_scores,
            "_usage": usage,
        }

    def _to_item_score(self, result: CodeGraderResult) -> dict[str, Any]:
        return {
            "item_code": result.item_code,
            "score": result.score,
            "max_score": result.max_score,
            "evidence": result.evidence,
            "rationale": result.rationale,
            "metrics": result.metrics,
            "confidence": "high",
        }

    def _evaluate_readme_quality(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        readme = repo_context.get("readme", "")
        readme_length = len(readme)

        if not readme or readme_length == 0:
            return CodeGraderResult(
                item_code="D1",
                score=0,
                max_score=6,
                evidence=["README 파일이 없습니다"],
                rationale="README 파일이 존재하지 않아 문서화 점수가 0점입니다",
                metrics={"readme_exists": False, "readme_length": 0},
            )

        score = 0
        evidence = []
        metrics = {"readme_exists": True, "readme_length": readme_length}

        score += 1
        evidence.append(f"README 파일 존재 ({readme_length} 문자)")

        if readme_length >= 500:
            score += 1
            evidence.append("README 길이 500자 이상")

        if readme_length >= 2000:
            score += 1
            evidence.append("README 길이 2000자 이상")

        readme_lower = readme.lower()

        install_patterns = [
            "installation",
            "install",
            "설치",
            "getting started",
            "시작하기",
            "quick start",
        ]
        has_install = any(p in readme_lower for p in install_patterns)
        if has_install:
            score += 1
            evidence.append("설치 섹션 포함")
        metrics["has_installation"] = has_install

        usage_patterns = [
            "usage",
            "how to use",
            "사용법",
            "사용 방법",
            "examples",
            "예제",
        ]
        has_usage = any(p in readme_lower for p in usage_patterns)
        if has_usage:
            score += 1
            evidence.append("사용법 섹션 포함")
        metrics["has_usage"] = has_usage

        env_patterns = [
            "environment",
            "env",
            "configuration",
            "config",
            "환경 변수",
            ".env",
        ]
        has_env = any(p in readme_lower for p in env_patterns)
        if has_env:
            score += 1
            evidence.append("환경 설정 섹션 포함")
        metrics["has_environment"] = has_env

        return CodeGraderResult(
            item_code="D1",
            score=min(score, 6),
            max_score=6,
            evidence=evidence,
            rationale=f"README 품질 평가: {score}/6점",
            metrics=metrics,
        )

    def _evaluate_code_comments(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        main_files = repo_context.get("main_files", [])

        if not main_files:
            return CodeGraderResult(
                item_code="D2",
                score=0,
                max_score=4,
                evidence=["분석할 코드 파일이 없습니다"],
                rationale="코드 파일이 제공되지 않아 주석 분석이 불가능합니다",
                metrics={"files_analyzed": 0},
            )

        total_lines = 0
        comment_lines = 0
        has_docstrings = False
        has_type_hints = False
        evidence = []

        for file_info in main_files:
            content = file_info.get("content", "")
            if not content:
                continue

            lines = content.split("\n")
            total_lines += len(lines)

            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("//"):
                    comment_lines += 1
                if "/*" in stripped or "*/" in stripped or stripped.startswith("*"):
                    comment_lines += 1

            if '"""' in content or "'''" in content:
                has_docstrings = True

            if "/**" in content and "@param" in content:
                has_docstrings = True

            if re.search(r"def\s+\w+\([^)]*:\s*\w+", content):
                has_type_hints = True
            if re.search(r"->\s*\w+:", content):
                has_type_hints = True
            if re.search(r":\s*(string|number|boolean|any|void)\b", content):
                has_type_hints = True

        if total_lines == 0:
            return CodeGraderResult(
                item_code="D2",
                score=0,
                max_score=4,
                evidence=["코드 내용이 비어있습니다"],
                rationale="코드 파일 내용이 없어 분석이 불가능합니다",
                metrics={"files_analyzed": len(main_files), "total_lines": 0},
            )

        comment_ratio = (comment_lines / total_lines) * 100 if total_lines > 0 else 0

        score = 0
        metrics = {
            "files_analyzed": len(main_files),
            "total_lines": total_lines,
            "comment_lines": comment_lines,
            "comment_ratio": round(comment_ratio, 2),
            "has_docstrings": has_docstrings,
            "has_type_hints": has_type_hints,
        }

        if comment_lines > 0:
            score += 1
            evidence.append(f"주석 {comment_lines}줄 발견")

        if comment_ratio >= 5:
            score += 1
            evidence.append(f"주석 비율 {comment_ratio:.1f}%")

        if has_docstrings:
            score += 1
            evidence.append("Docstring/JSDoc 사용")

        if has_type_hints:
            score += 1
            evidence.append("타입 힌트 사용")

        if not evidence:
            evidence.append("문서화 요소 없음")

        return CodeGraderResult(
            item_code="D2",
            score=min(score, 4),
            max_score=4,
            evidence=evidence,
            rationale=f"코드 주석 평가: {score}/4점",
            metrics=metrics,
        )

    def _evaluate_test_existence(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        file_tree = repo_context.get("file_tree", [])

        score = 0
        evidence = []
        metrics = {"has_tests": False, "has_ci": False, "test_file_count": 0}

        test_patterns = ["test_", "_test.", ".test.", ".spec.", "tests/", "__tests__/"]
        test_file_count = sum(
            1 for path in file_tree if any(p in path.lower() for p in test_patterns)
        )
        metrics["test_file_count"] = test_file_count

        if test_file_count > 0:
            score += 1
            evidence.append(f"테스트 파일 {test_file_count}개 발견")
            metrics["has_tests"] = True

        ci_patterns = [
            ".github/workflows/",
            ".gitlab-ci",
            "Jenkinsfile",
            ".circleci/",
            ".travis.yml",
        ]
        has_ci = any(any(p in path for p in ci_patterns) for path in file_tree)
        if has_ci:
            score += 1
            evidence.append("CI 설정 파일 존재")
            metrics["has_ci"] = True

        if test_file_count >= 3:
            score += 1
            evidence.append("다수의 테스트 파일 (3개 이상)")

        framework_files = {
            "pytest.ini": "pytest",
            "pyproject.toml": "pytest",
            "jest.config.js": "jest",
            "jest.config.ts": "jest",
            "vitest.config.js": "vitest",
            "vitest.config.ts": "vitest",
            "cypress.config.js": "cypress",
            "playwright.config.ts": "playwright",
        }

        filenames = {path.split("/")[-1].lower() for path in file_tree}
        detected_frameworks = [
            fw
            for filename, fw in framework_files.items()
            if filename.lower() in filenames
        ]
        metrics["test_frameworks"] = list(set(detected_frameworks))

        if detected_frameworks:
            score += 1
            evidence.append(f"테스트 프레임워크: {', '.join(set(detected_frameworks))}")

        if not evidence:
            evidence.append("테스트 관련 파일 없음")

        return CodeGraderResult(
            item_code="C4",
            score=min(score, 4),
            max_score=4,
            evidence=evidence,
            rationale=f"테스트 존재 평가: {score}/4점",
            metrics=metrics,
        )

    def _evaluate_tech_stack(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        file_tree = repo_context.get("file_tree", [])
        metadata = repo_context.get("metadata", {})
        languages = repo_context.get("languages", {})

        primary_language = metadata.get("language", "")
        if not primary_language and languages:
            primary_language = (
                max(languages.items(), key=lambda x: x[1])[0] if languages else ""
            )

        score = 0
        evidence = []
        metrics = {
            "primary_language": primary_language,
            "dependency_types": [],
            "total_packages": 0,
        }

        filenames = {path.split("/")[-1].lower() for path in file_tree}

        package_files = {
            "package.json": "npm",
            "requirements.txt": "pip",
            "pyproject.toml": "pip",
            "go.mod": "go",
            "Cargo.toml": "cargo",
            "Gemfile": "bundler",
            "build.gradle": "gradle",
            "pom.xml": "maven",
        }

        detected_pkg_managers = [
            pm
            for filename, pm in package_files.items()
            if filename.lower() in filenames
        ]
        metrics["dependency_types"] = list(set(detected_pkg_managers))

        if detected_pkg_managers:
            score += 1
            evidence.append(f"패키지 관리자: {', '.join(set(detected_pkg_managers))}")

        if primary_language:
            score += 1
            evidence.append(f"주요 언어: {primary_language}")

        if len(set(detected_pkg_managers)) >= 2:
            score += 1
            evidence.append("다중 패키지 관리자 사용 (폴리글랏)")

        modern_framework_indicators = [
            "next.config",
            "nuxt.config",
            "vite.config",
            "fastapi",
            "django",
            "flask",
        ]
        has_modern = any(
            any(ind in f.lower() for ind in modern_framework_indicators)
            for f in file_tree
        )
        if has_modern:
            score += 2
            evidence.append("모던 프레임워크 사용")

        if not evidence:
            evidence.append("기술 스택 정보 부족")

        return CodeGraderResult(
            item_code="B1",
            score=min(score, 7),
            max_score=7,
            evidence=evidence,
            rationale=f"기술 스택 평가: {score}/7점",
            metrics=metrics,
        )

    def _evaluate_system_architecture(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        file_tree = repo_context.get("file_tree", [])
        readme = repo_context.get("readme", "")

        if not file_tree:
            return CodeGraderResult(
                item_code="B2",
                score=0,
                max_score=6,
                evidence=["파일 구조 정보 없음"],
                rationale="파일 구조가 제공되지 않아 아키텍처 분석이 불가능합니다",
                metrics={
                    "folder_organization": False,
                    "modular_structure": False,
                    "static_analysis_tools": [],
                    "type_checking": False,
                    "architecture_docs": False,
                },
            )

        score = 0
        evidence = []
        metrics = {
            "folder_organization": False,
            "modular_structure": False,
            "static_analysis_tools": [],
            "type_checking": False,
            "architecture_docs": False,
        }

        organized_patterns = ["src/", "app/", "lib/", "pkg/", "cmd/", "internal/"]
        has_organized = any(
            any(path.startswith(p) or f"/{p}" in path for p in organized_patterns)
            for path in file_tree
        )
        if has_organized:
            score += 1
            evidence.append("정리된 폴더 구조 (src/, app/ 등)")
            metrics["folder_organization"] = True

        modular_patterns = [
            "components/",
            "services/",
            "models/",
            "utils/",
            "helpers/",
            "middleware/",
            "routes/",
            "controllers/",
            "handlers/",
            "api/",
        ]
        modular_count = sum(
            1
            for pattern in modular_patterns
            if any(pattern in path.lower() for path in file_tree)
        )
        if modular_count >= 2:
            score += 1
            evidence.append(f"모듈화된 구조 ({modular_count}개 패턴)")
            metrics["modular_structure"] = True
            metrics["modular_patterns_count"] = modular_count

        filenames = {path.split("/")[-1].lower() for path in file_tree}

        static_analysis_configs = {
            "ruff.toml": "ruff",
            ".flake8": "flake8",
            ".pylintrc": "pylint",
            ".black.toml": "black",
            ".eslintrc": "eslint",
            ".eslintrc.js": "eslint",
            ".eslintrc.json": "eslint",
            "eslint.config.js": "eslint",
            ".prettierrc": "prettier",
            ".prettierrc.js": "prettier",
            ".prettierrc.json": "prettier",
            "biome.json": "biome",
            ".golangci.yml": "golangci-lint",
        }

        detected_tools = {
            tool
            for config, tool in static_analysis_configs.items()
            if config.lower() in filenames
        }
        metrics["static_analysis_tools"] = list(detected_tools)

        if len(detected_tools) >= 2:
            score += 2
            evidence.append(f"정적 분석 도구: {', '.join(detected_tools)}")
        elif len(detected_tools) == 1:
            score += 1
            evidence.append(f"정적 분석 도구: {list(detected_tools)[0]}")

        type_configs = {
            "mypy.ini",
            ".mypy.ini",
            "pyrightconfig.json",
            "tsconfig.json",
            "jsconfig.json",
        }
        has_type_check = any(cfg.lower() in filenames for cfg in type_configs)
        if has_type_check:
            score += 1
            evidence.append("타입 체킹 설정 존재")
            metrics["type_checking"] = True

        arch_patterns = [
            "architecture.md",
            "architecture/",
            "docs/architecture",
            "docs/adr",
            "adr/",
            "design.md",
            "design/",
        ]
        has_arch_docs = any(
            any(p in path.lower() for p in arch_patterns) for path in file_tree
        )

        readme_lower = readme.lower() if readme else ""
        arch_readme_patterns = [
            "## architecture",
            "## 아키텍처",
            "## system design",
            "## 시스템 구조",
            "```mermaid",
            "```plantuml",
        ]
        has_arch_in_readme = any(p in readme_lower for p in arch_readme_patterns)

        if has_arch_docs or has_arch_in_readme:
            score += 1
            evidence.append("아키텍처 문서 존재")
            metrics["architecture_docs"] = True

        if not evidence:
            evidence.append("아키텍처 관련 설정 없음")

        return CodeGraderResult(
            item_code="B2",
            score=min(score, 6),
            max_score=6,
            evidence=evidence,
            rationale=f"시스템 아키텍처 평가: {score}/6점",
            metrics=metrics,
        )

    def _evaluate_code_quality(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        """Evaluate code quality (C1) based on linting configs and code metrics."""
        file_tree = repo_context.get("file_tree", [])
        main_files = repo_context.get("main_files", [])

        score = 0
        evidence = []
        metrics = {
            "has_linter_config": False,
            "has_formatter_config": False,
            "has_type_checker": False,
            "avg_file_length": 0,
            "total_files": len(main_files),
        }

        filenames = {path.split("/")[-1].lower() for path in file_tree}

        linter_configs = {
            "ruff.toml": "ruff",
            ".flake8": "flake8",
            ".pylintrc": "pylint",
            ".eslintrc": "eslint",
            ".eslintrc.js": "eslint",
            ".eslintrc.json": "eslint",
            "eslint.config.js": "eslint",
            ".golangci.yml": "golangci-lint",
        }
        detected_linters = [
            tool for cfg, tool in linter_configs.items() if cfg.lower() in filenames
        ]
        if detected_linters:
            score += 2
            evidence.append(f"린터 설정: {', '.join(set(detected_linters))}")
            metrics["has_linter_config"] = True

        formatter_configs = {
            ".prettierrc": "prettier",
            ".prettierrc.js": "prettier",
            ".prettierrc.json": "prettier",
            "biome.json": "biome",
            "black.toml": "black",
            "pyproject.toml": "black/isort",
        }
        detected_formatters = [
            tool for cfg, tool in formatter_configs.items() if cfg.lower() in filenames
        ]
        if detected_formatters:
            score += 1
            evidence.append(f"포맷터 설정: {', '.join(set(detected_formatters))}")
            metrics["has_formatter_config"] = True

        type_configs = {
            "mypy.ini": "mypy",
            ".mypy.ini": "mypy",
            "pyrightconfig.json": "pyright",
            "tsconfig.json": "typescript",
        }
        detected_type_checkers = [
            tool for cfg, tool in type_configs.items() if cfg.lower() in filenames
        ]
        if detected_type_checkers:
            score += 2
            evidence.append(f"타입 체커: {', '.join(set(detected_type_checkers))}")
            metrics["has_type_checker"] = True

        if main_files:
            total_lines = 0
            for file_info in main_files:
                content = file_info.get("content", "")
                if content:
                    total_lines += len(content.split("\n"))

            avg_length = total_lines / len(main_files) if main_files else 0
            metrics["avg_file_length"] = round(avg_length, 2)

            if avg_length <= 300:
                score += 1
                evidence.append(f"적절한 파일 길이 (평균 {avg_length:.0f}줄)")
            elif avg_length <= 500:
                score += 1
                evidence.append(f"양호한 파일 길이 (평균 {avg_length:.0f}줄)")

        if ".pre-commit-config.yaml" in filenames:
            score += 1
            evidence.append("pre-commit 훅 설정")

        if not evidence:
            evidence.append("코드 품질 도구 설정 없음")

        return CodeGraderResult(
            item_code="C1",
            score=min(score, 7),
            max_score=7,
            evidence=evidence,
            rationale=f"코드 품질 평가: {score}/7점",
            metrics=metrics,
        )

    def _evaluate_testing_coverage(
        self, repo_context: dict[str, Any]
    ) -> CodeGraderResult | None:
        """Evaluate testing coverage (C2) based on test files and coverage configs."""
        file_tree = repo_context.get("file_tree", [])

        score = 0
        evidence = []
        metrics = {
            "test_file_count": 0,
            "has_coverage_config": False,
            "has_test_framework": False,
            "test_to_source_ratio": 0.0,
        }

        test_patterns = ["test_", "_test.", ".test.", ".spec."]
        test_files = [
            path for path in file_tree if any(p in path.lower() for p in test_patterns)
        ]
        test_file_count = len(test_files)
        metrics["test_file_count"] = test_file_count

        if test_file_count > 0:
            score += 1
            evidence.append(f"테스트 파일 {test_file_count}개")

        if test_file_count >= 5:
            score += 1
            evidence.append("충분한 테스트 파일 (5개 이상)")

        coverage_configs = [
            ".coveragerc",
            "coverage.ini",
            ".nycrc",
            "codecov.yml",
            ".codecov.yml",
        ]
        has_coverage = any(
            cfg in path.lower() for path in file_tree for cfg in coverage_configs
        )
        if has_coverage:
            score += 2
            evidence.append("커버리지 설정 존재")
            metrics["has_coverage_config"] = True

        framework_configs = {
            "pytest.ini": "pytest",
            "setup.cfg": "pytest/distutils",
            "jest.config.js": "jest",
            "jest.config.ts": "jest",
            "vitest.config.js": "vitest",
            "vitest.config.ts": "vitest",
            "karma.conf.js": "karma",
        }
        filenames = {path.split("/")[-1].lower() for path in file_tree}
        detected_frameworks = [
            fw for cfg, fw in framework_configs.items() if cfg.lower() in filenames
        ]
        if detected_frameworks:
            score += 1
            evidence.append(f"테스트 프레임워크: {', '.join(set(detected_frameworks))}")
            metrics["has_test_framework"] = True

        source_files = [
            f
            for f in file_tree
            if f.endswith((".py", ".js", ".ts", ".go", ".java", ".rs"))
            and not any(
                p in f.lower() for p in test_patterns + ["tests/", "__tests__/"]
            )
        ]
        if source_files and test_files:
            ratio = len(test_files) / len(source_files)
            metrics["test_to_source_ratio"] = round(ratio, 2)
            if ratio >= 0.5:
                score += 1
                evidence.append(f"양호한 테스트 비율 ({ratio:.2f})")

        if not evidence:
            evidence.append("테스트 관련 설정 부족")

        return CodeGraderResult(
            item_code="C2",
            score=min(score, 6),
            max_score=6,
            evidence=evidence,
            rationale=f"테스트 커버리지 평가: {score}/6점",
            metrics=metrics,
        )
