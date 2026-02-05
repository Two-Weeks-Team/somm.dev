"""Codebase analyzer for AST-based code metrics extraction.

Phase 2.7-2.9: Codebase Analyzer with tree-sitter support for 9 languages.
Uses tree-sitter for structural parsing and radon for Python-specific metrics.
"""

import logging
import re
import threading
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)


@dataclass
class FunctionMetric:
    """Individual function/method metrics."""

    name: str
    file_path: str
    line_start: int
    line_end: int
    cyclomatic_complexity: int
    parameters: int = 0
    lines_of_code: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "parameters": self.parameters,
            "lines_of_code": self.lines_of_code,
        }


@dataclass
class FileMetrics:
    """Metrics for a single file."""

    path: str
    language: str
    lines_of_code: int = 0
    lines_of_comments: int = 0
    functions: list[FunctionMetric] = field(default_factory=list)
    classes: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    maintainability_index: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "language": self.language,
            "lines_of_code": self.lines_of_code,
            "lines_of_comments": self.lines_of_comments,
            "functions": [f.to_dict() for f in self.functions],
            "classes": self.classes,
            "avg_complexity": self.avg_complexity,
            "max_complexity": self.max_complexity,
            "maintainability_index": self.maintainability_index,
            "error": self.error,
        }


@dataclass
class CodeMetrics:
    """Aggregate code metrics for a codebase."""

    total_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    avg_cyclomatic_complexity: float = 0.0
    max_cyclomatic_complexity: int = 0
    maintainability_index: float = 0.0
    language_breakdown: dict[str, int] = field(default_factory=dict)
    complexity_distribution: dict[str, int] = field(default_factory=dict)
    large_functions: list[FunctionMetric] = field(default_factory=list)
    high_complexity_functions: list[FunctionMetric] = field(default_factory=list)
    file_metrics: list[FileMetrics] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_functions": self.total_functions,
            "total_classes": self.total_classes,
            "avg_cyclomatic_complexity": round(self.avg_cyclomatic_complexity, 2),
            "max_cyclomatic_complexity": self.max_cyclomatic_complexity,
            "maintainability_index": round(self.maintainability_index, 2),
            "language_breakdown": self.language_breakdown,
            "complexity_distribution": self.complexity_distribution,
            "large_functions": [f.to_dict() for f in self.large_functions[:10]],
            "high_complexity_functions": [
                f.to_dict() for f in self.high_complexity_functions[:10]
            ],
            "errors": self.errors[:5],
        }


LanguageType = Literal[
    "python",
    "javascript",
    "typescript",
    "tsx",
    "go",
    "ruby",
    "kotlin",
    "swift",
    "dart",
    "unknown",
]


class CodebaseAnalyzer:
    """Analyze codebases using AST-based metrics.

    Thread-safe singleton pattern with thread-local parsers.
    Supports 9 languages: Python, JavaScript, TypeScript, TSX, Go, Ruby, Kotlin, Swift, Dart.
    """

    _instance: "CodebaseAnalyzer | None" = None
    _lock = threading.Lock()
    _languages_initialized = False

    _py_language: Any = None
    _js_language: Any = None
    _ts_language: Any = None
    _tsx_language: Any = None
    _go_language: Any = None
    _ruby_language: Any = None
    _kotlin_language: Any = None
    _swift_language: Any = None
    _dart_language: Any = None

    _thread_local = threading.local()

    def __new__(cls) -> "CodebaseAnalyzer":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        pass

    def _ensure_languages(self) -> bool:
        if self._languages_initialized:
            return True

        with self._lock:
            if self._languages_initialized:
                return True

            try:
                from tree_sitter import Language
                import tree_sitter_python
                import tree_sitter_javascript
                import tree_sitter_typescript

                self._py_language = Language(tree_sitter_python.language())
                self._js_language = Language(tree_sitter_javascript.language())
                self._ts_language = Language(
                    tree_sitter_typescript.language_typescript()
                )
                self._tsx_language = Language(tree_sitter_typescript.language_tsx())

                try:
                    import tree_sitter_go

                    self._go_language = Language(tree_sitter_go.language())
                except ImportError:
                    logger.debug("tree-sitter-go not available")

                try:
                    import tree_sitter_ruby

                    self._ruby_language = Language(tree_sitter_ruby.language())
                except ImportError:
                    logger.debug("tree-sitter-ruby not available")

                try:
                    import tree_sitter_kotlin

                    self._kotlin_language = Language(tree_sitter_kotlin.language())
                except ImportError:
                    logger.debug("tree-sitter-kotlin not available")

                try:
                    import tree_sitter_swift

                    self._swift_language = Language(tree_sitter_swift.language())
                except ImportError:
                    logger.debug("tree-sitter-swift not available")

                try:
                    import tree_sitter_dart_orchard

                    self._dart_language = Language(tree_sitter_dart_orchard.language())
                except ImportError:
                    logger.debug("tree-sitter-dart-orchard not available")

                self._languages_initialized = True
                logger.info("Tree-sitter languages initialized successfully")
                return True

            except ImportError as e:
                logger.warning(f"Tree-sitter not available: {e}")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize tree-sitter: {e}")
                return False

    def _get_parser(self, lang_type: str) -> Any:
        if not self._ensure_languages():
            return None

        if not hasattr(self._thread_local, "parsers"):
            self._thread_local.parsers = {}

        if lang_type not in self._thread_local.parsers:
            try:
                from tree_sitter import Parser

                language_map = {
                    "python": self._py_language,
                    "javascript": self._js_language,
                    "typescript": self._ts_language,
                    "tsx": self._tsx_language,
                    "go": self._go_language,
                    "ruby": self._ruby_language,
                    "kotlin": self._kotlin_language,
                    "swift": self._swift_language,
                    "dart": self._dart_language,
                }
                language = language_map.get(lang_type)
                if language:
                    self._thread_local.parsers[lang_type] = Parser(language)
                    logger.debug(f"Created thread-local parser for {lang_type}")
            except Exception as e:
                logger.error(f"Failed to create parser for {lang_type}: {e}")
                return None

        return self._thread_local.parsers.get(lang_type)

    def _detect_language(self, path: str) -> LanguageType:
        path_lower = path.lower()
        if path_lower.endswith(".py"):
            return "python"
        elif path_lower.endswith(".tsx"):
            return "tsx"
        elif path_lower.endswith(".ts"):
            return "typescript"
        elif path_lower.endswith((".js", ".jsx", ".mjs", ".cjs")):
            return "javascript"
        elif path_lower.endswith(".go"):
            return "go"
        elif path_lower.endswith(".rb"):
            return "ruby"
        elif path_lower.endswith((".kt", ".kts")):
            return "kotlin"
        elif path_lower.endswith(".swift"):
            return "swift"
        elif path_lower.endswith(".dart"):
            return "dart"
        return "unknown"

    def analyze_file(self, content: str, path: str) -> FileMetrics:
        language = self._detect_language(path)

        if language == "python":
            return self._analyze_python_file(content, path)
        elif language in ("javascript", "typescript", "tsx"):
            return self._analyze_js_file(content, path, language)
        elif language == "go":
            return self._analyze_go_file(content, path)
        elif language == "ruby":
            return self._analyze_ruby_file(content, path)
        elif language == "kotlin":
            return self._analyze_kotlin_file(content, path)
        elif language == "swift":
            return self._analyze_swift_file(content, path)
        elif language == "dart":
            return self._analyze_dart_file(content, path)
        else:
            return FileMetrics(
                path=path,
                language="unknown",
                lines_of_code=len(content.splitlines()),
            )

    def _analyze_python_file(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="python")

        try:
            from radon.complexity import cc_visit
            from radon.metrics import mi_visit
            from radon.raw import analyze as radon_analyze

            try:
                raw = radon_analyze(content)
                metrics.lines_of_code = raw.loc
                metrics.lines_of_comments = raw.comments
            except Exception:
                metrics.lines_of_code = len(content.splitlines())

            try:
                cc_results = cc_visit(content)
                for block in cc_results:
                    func = FunctionMetric(
                        name=block.name,
                        file_path=path,
                        line_start=block.lineno,
                        line_end=block.endline,
                        cyclomatic_complexity=block.complexity,
                        lines_of_code=block.endline - block.lineno + 1,
                    )
                    metrics.functions.append(func)

                if metrics.functions:
                    complexities = [f.cyclomatic_complexity for f in metrics.functions]
                    metrics.avg_complexity = sum(complexities) / len(complexities)
                    metrics.max_complexity = max(complexities)
            except Exception:
                pass

            try:
                mi_result = mi_visit(content, multi=False)
                if isinstance(mi_result, (int, float)):
                    metrics.maintainability_index = float(mi_result)
            except Exception:
                pass

            py_parser = self._get_parser("python")
            if py_parser:
                try:
                    tree = py_parser.parse(bytes(content, "utf8"))
                    metrics.classes = self._count_nodes(
                        tree.root_node, "class_definition"
                    )
                except Exception:
                    pass

        except ImportError:
            metrics = self._analyze_python_fallback(content, path)
        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze Python file {path}: {e}")

        return metrics

    def _analyze_python_fallback(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="python")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        comment_pattern = re.compile(r"^\s*#")
        metrics.lines_of_comments = sum(
            1 for line in lines if comment_pattern.match(line)
        )

        func_pattern = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")
        class_pattern = re.compile(r"^\s*class\s+(\w+)")

        for i, line in enumerate(lines, 1):
            func_match = func_pattern.match(line)
            if func_match:
                metrics.functions.append(
                    FunctionMetric(
                        name=func_match.group(1),
                        file_path=path,
                        line_start=i,
                        line_end=i,
                        cyclomatic_complexity=1,
                    )
                )
            if class_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _analyze_js_file(self, content: str, path: str, language: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language=language)
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        parser = self._get_parser(language)
        if not parser:
            return self._analyze_js_fallback(content, path, language)

        try:
            tree = parser.parse(bytes(content, "utf8"))
            root = tree.root_node

            metrics.lines_of_comments = self._count_nodes(root, "comment")
            metrics.functions = self._extract_js_functions(root, path)
            metrics.classes = self._count_nodes(root, "class_declaration")

            if metrics.functions:
                complexities = [f.cyclomatic_complexity for f in metrics.functions]
                metrics.avg_complexity = sum(complexities) / len(complexities)
                metrics.max_complexity = max(complexities)

        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze JS/TS file {path}: {e}")

        return metrics

    def _analyze_js_fallback(
        self, content: str, path: str, language: str
    ) -> FileMetrics:
        metrics = FileMetrics(path=path, language=language)
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        func_patterns = [
            re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)"),
            re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\("),
            re.compile(r"^\s*(\w+)\s*\([^)]*\)\s*{"),
        ]
        class_pattern = re.compile(r"^\s*(?:export\s+)?class\s+(\w+)")

        for i, line in enumerate(lines, 1):
            for pattern in func_patterns:
                match = pattern.match(line)
                if match:
                    metrics.functions.append(
                        FunctionMetric(
                            name=match.group(1),
                            file_path=path,
                            line_start=i,
                            line_end=i,
                            cyclomatic_complexity=1,
                        )
                    )
                    break
            if class_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _extract_js_functions(self, node: Any, path: str) -> list[FunctionMetric]:
        functions: list[FunctionMetric] = []

        func_types = {
            "function_declaration",
            "function_expression",
            "arrow_function",
            "method_definition",
            "function",
        }

        stack = [node]
        while stack:
            current = stack.pop()
            if current.type in func_types:
                name = self._get_function_name(current)
                complexity = self._calculate_js_complexity(current)
                start_line = current.start_point[0] + 1
                end_line = current.end_point[0] + 1

                functions.append(
                    FunctionMetric(
                        name=name,
                        file_path=path,
                        line_start=start_line,
                        line_end=end_line,
                        cyclomatic_complexity=complexity,
                        lines_of_code=end_line - start_line + 1,
                    )
                )

            stack.extend(current.children)

        return functions

    def _get_function_name(self, node: Any) -> str:
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf8")
            if child.type == "property_identifier":
                return child.text.decode("utf8")

        if node.parent and node.parent.type == "variable_declarator":
            for child in node.parent.children:
                if child.type == "identifier":
                    return child.text.decode("utf8")

        return "<anonymous>"

    def _calculate_js_complexity(self, node: Any) -> int:
        decision_types = {
            "if_statement",
            "for_statement",
            "for_in_statement",
            "while_statement",
            "do_statement",
            "switch_case",
            "catch_clause",
            "ternary_expression",
            "conditional_expression",
        }

        nested_func_types = {
            "function_declaration",
            "function_expression",
            "arrow_function",
            "method_definition",
            "function",
        }

        logical_operators = {"&&", "||", "??"}

        decision_count = 0
        stack = list(node.children)

        while stack:
            current = stack.pop()

            if current.type in nested_func_types:
                continue

            if current.type in decision_types:
                decision_count += 1
            elif current.type == "binary_expression":
                for child in current.children:
                    if (
                        hasattr(child, "text")
                        and child.text.decode("utf8") in logical_operators
                    ):
                        decision_count += 1

            stack.extend(current.children)

        return 1 + decision_count

    def _analyze_go_file(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="go")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        go_parser = self._get_parser("go")
        if not go_parser:
            return self._analyze_go_fallback(content, path)

        try:
            tree = go_parser.parse(bytes(content, "utf8"))
            root = tree.root_node

            metrics.lines_of_comments = self._count_nodes(root, "comment")
            metrics.functions = self._extract_go_functions(root, path)
            metrics.classes = self._count_go_types(root)

            if metrics.functions:
                complexities = [f.cyclomatic_complexity for f in metrics.functions]
                metrics.avg_complexity = sum(complexities) / len(complexities)
                metrics.max_complexity = max(complexities)

        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze Go file {path}: {e}")

        return metrics

    def _analyze_go_fallback(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="go")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        comment_pattern = re.compile(r"^\s*//")
        metrics.lines_of_comments = sum(
            1 for line in lines if comment_pattern.match(line)
        )

        func_pattern = re.compile(r"^\s*func\s+(?:\([^)]+\)\s+)?(\w+)")
        type_pattern = re.compile(r"^\s*type\s+(\w+)\s+struct")

        for i, line in enumerate(lines, 1):
            func_match = func_pattern.match(line)
            if func_match:
                metrics.functions.append(
                    FunctionMetric(
                        name=func_match.group(1),
                        file_path=path,
                        line_start=i,
                        line_end=i,
                        cyclomatic_complexity=1,
                    )
                )
            if type_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _extract_go_functions(self, node: Any, path: str) -> list[FunctionMetric]:
        functions: list[FunctionMetric] = []
        func_types = {"function_declaration", "method_declaration"}

        stack = [node]
        while stack:
            current = stack.pop()
            if current.type in func_types:
                name = self._get_go_function_name(current)
                complexity = self._calculate_go_complexity(current)
                start_line = current.start_point[0] + 1
                end_line = current.end_point[0] + 1

                functions.append(
                    FunctionMetric(
                        name=name,
                        file_path=path,
                        line_start=start_line,
                        line_end=end_line,
                        cyclomatic_complexity=complexity,
                        lines_of_code=end_line - start_line + 1,
                    )
                )

            stack.extend(current.children)

        return functions

    def _get_go_function_name(self, node: Any) -> str:
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf8")
            if child.type == "field_identifier":
                return child.text.decode("utf8")
        return "<anonymous>"

    def _calculate_go_complexity(self, node: Any) -> int:
        decision_types = {
            "if_statement",
            "for_statement",
            "switch_statement",
            "type_switch_statement",
            "select_statement",
            "expression_case",
            "type_case",
            "default_case",
        }

        nested_func_types = {
            "function_declaration",
            "method_declaration",
            "func_literal",
        }
        logical_operators = {"&&", "||"}

        decision_count = 0
        stack = list(node.children)

        while stack:
            current = stack.pop()

            if current.type in nested_func_types and current != node:
                continue

            if current.type in decision_types:
                decision_count += 1
            elif current.type == "binary_expression":
                for child in current.children:
                    if (
                        hasattr(child, "text")
                        and child.text.decode("utf8") in logical_operators
                    ):
                        decision_count += 1

            stack.extend(current.children)

        return 1 + decision_count

    def _count_go_types(self, node: Any) -> int:
        count = 0
        stack = [node]
        while stack:
            current = stack.pop()
            if current.type == "type_declaration":
                for child in current.children:
                    if child.type in ("struct_type", "interface_type"):
                        count += 1
                        break
            stack.extend(current.children)
        return count

    def _analyze_ruby_file(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="ruby")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        ruby_parser = self._get_parser("ruby")
        if not ruby_parser:
            return self._analyze_ruby_fallback(content, path)

        try:
            tree = ruby_parser.parse(bytes(content, "utf8"))
            root = tree.root_node

            metrics.lines_of_comments = self._count_nodes(root, "comment")
            metrics.functions = self._extract_ruby_functions(root, path)
            metrics.classes = self._count_nodes(root, "class") + self._count_nodes(
                root, "module"
            )

            if metrics.functions:
                complexities = [f.cyclomatic_complexity for f in metrics.functions]
                metrics.avg_complexity = sum(complexities) / len(complexities)
                metrics.max_complexity = max(complexities)

        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze Ruby file {path}: {e}")

        return metrics

    def _analyze_ruby_fallback(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="ruby")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        comment_pattern = re.compile(r"^\s*#")
        metrics.lines_of_comments = sum(
            1 for line in lines if comment_pattern.match(line)
        )

        def_pattern = re.compile(r"^\s*def\s+(\w+)")
        class_pattern = re.compile(r"^\s*(?:class|module)\s+(\w+)")

        for i, line in enumerate(lines, 1):
            def_match = def_pattern.match(line)
            if def_match:
                metrics.functions.append(
                    FunctionMetric(
                        name=def_match.group(1),
                        file_path=path,
                        line_start=i,
                        line_end=i,
                        cyclomatic_complexity=1,
                    )
                )
            if class_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _extract_ruby_functions(self, node: Any, path: str) -> list[FunctionMetric]:
        functions: list[FunctionMetric] = []
        func_types = {"method", "singleton_method"}

        stack = [node]
        while stack:
            current = stack.pop()
            if current.type in func_types:
                name = self._get_ruby_method_name(current)
                complexity = self._calculate_ruby_complexity(current)
                start_line = current.start_point[0] + 1
                end_line = current.end_point[0] + 1

                functions.append(
                    FunctionMetric(
                        name=name,
                        file_path=path,
                        line_start=start_line,
                        line_end=end_line,
                        cyclomatic_complexity=complexity,
                        lines_of_code=end_line - start_line + 1,
                    )
                )

            stack.extend(current.children)

        return functions

    def _get_ruby_method_name(self, node: Any) -> str:
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf8")
        return "<anonymous>"

    def _calculate_ruby_complexity(self, node: Any) -> int:
        decision_types = {
            "if",
            "unless",
            "case",
            "for",
            "while",
            "until",
            "rescue",
            "when",
            "elsif",
        }

        nested_func_types = {"method", "singleton_method", "lambda", "block"}
        logical_operators = {"and", "or", "&&", "||"}

        decision_count = 0
        stack = list(node.children)

        while stack:
            current = stack.pop()

            if current.type in nested_func_types and current != node:
                continue

            if current.type in decision_types:
                decision_count += 1
            elif current.type == "binary":
                for child in current.children:
                    if (
                        hasattr(child, "text")
                        and child.text.decode("utf8") in logical_operators
                    ):
                        decision_count += 1

            stack.extend(current.children)

        return 1 + decision_count

    def _analyze_kotlin_file(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="kotlin")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        kotlin_parser = self._get_parser("kotlin")
        if not kotlin_parser:
            return self._analyze_kotlin_fallback(content, path)

        try:
            tree = kotlin_parser.parse(bytes(content, "utf8"))
            root = tree.root_node

            metrics.lines_of_comments = self._count_nodes(
                root, "line_comment"
            ) + self._count_nodes(root, "multiline_comment")
            metrics.functions = self._extract_kotlin_functions(root, path)
            metrics.classes = self._count_nodes(
                root, "class_declaration"
            ) + self._count_nodes(root, "object_declaration")

            if metrics.functions:
                complexities = [f.cyclomatic_complexity for f in metrics.functions]
                metrics.avg_complexity = sum(complexities) / len(complexities)
                metrics.max_complexity = max(complexities)

        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze Kotlin file {path}: {e}")

        return metrics

    def _analyze_kotlin_fallback(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="kotlin")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        comment_pattern = re.compile(r"^\s*//")
        metrics.lines_of_comments = sum(
            1 for line in lines if comment_pattern.match(line)
        )

        fun_pattern = re.compile(
            r"^\s*(?:private\s+|public\s+|internal\s+|protected\s+)?fun\s+(\w+)"
        )
        class_pattern = re.compile(r"^\s*(?:data\s+)?class\s+(\w+)")

        for i, line in enumerate(lines, 1):
            fun_match = fun_pattern.match(line)
            if fun_match:
                metrics.functions.append(
                    FunctionMetric(
                        name=fun_match.group(1),
                        file_path=path,
                        line_start=i,
                        line_end=i,
                        cyclomatic_complexity=1,
                    )
                )
            if class_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _extract_kotlin_functions(self, node: Any, path: str) -> list[FunctionMetric]:
        functions: list[FunctionMetric] = []

        stack = [node]
        while stack:
            current = stack.pop()
            if current.type == "function_declaration":
                name = self._get_kotlin_function_name(current)
                complexity = self._calculate_kotlin_complexity(current)
                start_line = current.start_point[0] + 1
                end_line = current.end_point[0] + 1

                functions.append(
                    FunctionMetric(
                        name=name,
                        file_path=path,
                        line_start=start_line,
                        line_end=end_line,
                        cyclomatic_complexity=complexity,
                        lines_of_code=end_line - start_line + 1,
                    )
                )

            stack.extend(current.children)

        return functions

    def _get_kotlin_function_name(self, node: Any) -> str:
        for child in node.children:
            if child.type == "simple_identifier":
                return child.text.decode("utf8")
        return "<anonymous>"

    def _calculate_kotlin_complexity(self, node: Any) -> int:
        decision_types = {
            "if_expression",
            "when_expression",
            "for_statement",
            "while_statement",
            "do_while_statement",
            "catch_clause",
            "when_entry",
        }

        nested_func_types = {
            "function_declaration",
            "lambda_literal",
            "anonymous_function",
        }

        decision_count = 0
        stack = list(node.children)

        while stack:
            current = stack.pop()

            if current.type in nested_func_types and current != node:
                continue

            if current.type in decision_types:
                decision_count += 1
            elif current.type in ("conjunction_expression", "disjunction_expression"):
                decision_count += 1
            elif current.type == "elvis_expression":
                decision_count += 1

            stack.extend(current.children)

        return 1 + decision_count

    def _analyze_swift_file(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="swift")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        swift_parser = self._get_parser("swift")
        if not swift_parser:
            return self._analyze_swift_fallback(content, path)

        try:
            tree = swift_parser.parse(bytes(content, "utf8"))
            root = tree.root_node

            metrics.lines_of_comments = self._count_nodes(
                root, "comment"
            ) + self._count_nodes(root, "multiline_comment")
            metrics.functions = self._extract_swift_functions(root, path)
            metrics.classes = (
                self._count_nodes(root, "class_declaration")
                + self._count_nodes(root, "struct_declaration")
                + self._count_nodes(root, "protocol_declaration")
            )

            if metrics.functions:
                complexities = [f.cyclomatic_complexity for f in metrics.functions]
                metrics.avg_complexity = sum(complexities) / len(complexities)
                metrics.max_complexity = max(complexities)

        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze Swift file {path}: {e}")

        return metrics

    def _analyze_swift_fallback(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="swift")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        comment_pattern = re.compile(r"^\s*//")
        metrics.lines_of_comments = sum(
            1 for line in lines if comment_pattern.match(line)
        )

        func_pattern = re.compile(
            r"^\s*(?:private\s+|public\s+|internal\s+)?func\s+(\w+)"
        )
        class_pattern = re.compile(r"^\s*(?:class|struct|protocol)\s+(\w+)")

        for i, line in enumerate(lines, 1):
            func_match = func_pattern.match(line)
            if func_match:
                metrics.functions.append(
                    FunctionMetric(
                        name=func_match.group(1),
                        file_path=path,
                        line_start=i,
                        line_end=i,
                        cyclomatic_complexity=1,
                    )
                )
            if class_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _extract_swift_functions(self, node: Any, path: str) -> list[FunctionMetric]:
        functions: list[FunctionMetric] = []

        stack = [node]
        while stack:
            current = stack.pop()
            if current.type == "function_declaration":
                name = self._get_swift_function_name(current)
                complexity = self._calculate_swift_complexity(current)
                start_line = current.start_point[0] + 1
                end_line = current.end_point[0] + 1

                functions.append(
                    FunctionMetric(
                        name=name,
                        file_path=path,
                        line_start=start_line,
                        line_end=end_line,
                        cyclomatic_complexity=complexity,
                        lines_of_code=end_line - start_line + 1,
                    )
                )

            stack.extend(current.children)

        return functions

    def _get_swift_function_name(self, node: Any) -> str:
        for child in node.children:
            if child.type == "simple_identifier":
                return child.text.decode("utf8")
        return "<anonymous>"

    def _calculate_swift_complexity(self, node: Any) -> int:
        decision_types = {
            "if_statement",
            "guard_statement",
            "for_statement",
            "while_statement",
            "repeat_while_statement",
            "switch_statement",
            "catch_clause",
            "case_clause",
        }

        nested_func_types = {"function_declaration", "closure_expression"}

        decision_count = 0
        stack = list(node.children)

        while stack:
            current = stack.pop()

            if current.type in nested_func_types and current != node:
                continue

            if current.type in decision_types:
                decision_count += 1
            elif current.type == "ternary_expression":
                decision_count += 1

            stack.extend(current.children)

        return 1 + decision_count

    def _analyze_dart_file(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="dart")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        dart_parser = self._get_parser("dart")
        if not dart_parser:
            return self._analyze_dart_fallback(content, path)

        try:
            tree = dart_parser.parse(bytes(content, "utf8"))
            root = tree.root_node

            metrics.lines_of_comments = self._count_nodes(
                root, "comment"
            ) + self._count_nodes(root, "documentation_comment")
            metrics.functions = self._extract_dart_functions(root, path)
            metrics.classes = self._count_nodes(root, "class_definition")

            if metrics.functions:
                complexities = [f.cyclomatic_complexity for f in metrics.functions]
                metrics.avg_complexity = sum(complexities) / len(complexities)
                metrics.max_complexity = max(complexities)

        except Exception as e:
            metrics.error = str(e)
            logger.warning(f"Failed to analyze Dart file {path}: {e}")

        return metrics

    def _analyze_dart_fallback(self, content: str, path: str) -> FileMetrics:
        metrics = FileMetrics(path=path, language="dart")
        lines = content.splitlines()
        metrics.lines_of_code = len(lines)

        comment_pattern = re.compile(r"^\s*//")
        metrics.lines_of_comments = sum(
            1 for line in lines if comment_pattern.match(line)
        )

        func_pattern = re.compile(
            r"^\s*(?:void|int|String|bool|Future|Stream|\w+)\s+(\w+)\s*\("
        )
        class_pattern = re.compile(r"^\s*class\s+(\w+)")

        for i, line in enumerate(lines, 1):
            func_match = func_pattern.match(line)
            if func_match:
                metrics.functions.append(
                    FunctionMetric(
                        name=func_match.group(1),
                        file_path=path,
                        line_start=i,
                        line_end=i,
                        cyclomatic_complexity=1,
                    )
                )
            if class_pattern.match(line):
                metrics.classes += 1

        if metrics.functions:
            metrics.avg_complexity = 1.0
            metrics.max_complexity = 1

        return metrics

    def _extract_dart_functions(self, node: Any, path: str) -> list[FunctionMetric]:
        functions: list[FunctionMetric] = []
        func_types = {"function_declaration", "method_signature"}

        stack = [node]
        while stack:
            current = stack.pop()
            if current.type in func_types:
                name = self._get_dart_function_name(current)
                complexity = self._calculate_dart_complexity(current)
                start_line = current.start_point[0] + 1
                end_line = current.end_point[0] + 1

                functions.append(
                    FunctionMetric(
                        name=name,
                        file_path=path,
                        line_start=start_line,
                        line_end=end_line,
                        cyclomatic_complexity=complexity,
                        lines_of_code=end_line - start_line + 1,
                    )
                )

            stack.extend(current.children)

        return functions

    def _get_dart_function_name(self, node: Any) -> str:
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf8")
        return "<anonymous>"

    def _calculate_dart_complexity(self, node: Any) -> int:
        decision_types = {
            "if_statement",
            "for_statement",
            "while_statement",
            "do_statement",
            "switch_statement",
            "catch_clause",
            "case_clause",
        }

        nested_func_types = {"function_declaration", "function_expression"}

        decision_count = 0
        stack = list(node.children)

        while stack:
            current = stack.pop()

            if current.type in nested_func_types and current != node:
                continue

            if current.type in decision_types:
                decision_count += 1
            elif current.type == "conditional_expression":
                decision_count += 1

            stack.extend(current.children)

        return 1 + decision_count

    def _count_nodes(self, node: Any, node_type: str) -> int:
        count = 0
        stack = [node]
        while stack:
            current = stack.pop()
            if current.type == node_type:
                count += 1
            stack.extend(current.children)
        return count

    def analyze_files(self, main_files: list[dict[str, str]]) -> CodeMetrics:
        metrics = CodeMetrics()
        all_functions: list[FunctionMetric] = []

        for file_info in main_files:
            path = file_info.get("path", "")
            content = file_info.get("content", "")

            if not content:
                continue

            language = self._detect_language(path)
            if language == "unknown":
                continue

            try:
                file_metrics = self.analyze_file(content, path)

                metrics.total_files += 1
                metrics.total_lines += file_metrics.lines_of_code
                metrics.total_classes += file_metrics.classes
                metrics.total_functions += len(file_metrics.functions)
                all_functions.extend(file_metrics.functions)
                metrics.file_metrics.append(file_metrics)

                lang_key = file_metrics.language
                metrics.language_breakdown[lang_key] = (
                    metrics.language_breakdown.get(lang_key, 0)
                    + file_metrics.lines_of_code
                )

                if file_metrics.error:
                    metrics.errors.append(f"{path}: {file_metrics.error}")

            except Exception as e:
                metrics.errors.append(f"{path}: {e}")
                logger.warning(f"Failed to analyze {path}: {e}")

        if all_functions:
            complexities = [f.cyclomatic_complexity for f in all_functions]
            metrics.avg_cyclomatic_complexity = sum(complexities) / len(complexities)
            metrics.max_cyclomatic_complexity = max(complexities)

            for grade in ["A", "B", "C", "D", "E", "F"]:
                metrics.complexity_distribution[grade] = 0
            for cc in complexities:
                grade = self._get_complexity_grade(cc)
                metrics.complexity_distribution[grade] = (
                    metrics.complexity_distribution.get(grade, 0) + 1
                )

            metrics.high_complexity_functions = sorted(
                [f for f in all_functions if f.cyclomatic_complexity > 10],
                key=lambda x: x.cyclomatic_complexity,
                reverse=True,
            )[:10]

            metrics.large_functions = sorted(
                [f for f in all_functions if f.lines_of_code > 50],
                key=lambda x: x.lines_of_code,
                reverse=True,
            )[:10]

        mi_values = [
            fm.maintainability_index
            for fm in metrics.file_metrics
            if fm.maintainability_index is not None
        ]
        if mi_values:
            metrics.maintainability_index = sum(mi_values) / len(mi_values)

        return metrics

    def _get_complexity_grade(self, cc: int) -> str:
        if cc <= 5:
            return "A"
        elif cc <= 10:
            return "B"
        elif cc <= 20:
            return "C"
        elif cc <= 30:
            return "D"
        elif cc <= 40:
            return "E"
        return "F"


codebase_analyzer = CodebaseAnalyzer()
