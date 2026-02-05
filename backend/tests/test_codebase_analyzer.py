"""Tests for Codebase Analyzer - AST-based code metrics extraction.

Phase 2.7-2.9: Codebase Analyzer with tree-sitter support
"""

import pytest
import threading
from typing import Any


class TestCodebaseAnalyzerImports:
    def test_import_codebase_analyzer_module(self):
        from app.processors import codebase_analyzer

        assert codebase_analyzer is not None

    def test_import_file_metrics(self):
        from app.processors.codebase_analyzer import FileMetrics

        assert FileMetrics is not None

    def test_import_code_metrics(self):
        from app.processors.codebase_analyzer import CodeMetrics

        assert CodeMetrics is not None

    def test_import_codebase_analyzer_class(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        assert CodebaseAnalyzer is not None


class TestCodebaseAnalyzerSingleton:
    def test_singleton_instance(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        a1 = CodebaseAnalyzer()
        a2 = CodebaseAnalyzer()
        assert a1 is a2

    def test_thread_safety(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        instances = []

        def create_instance():
            instances.append(CodebaseAnalyzer())

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(inst is instances[0] for inst in instances)


class TestFileMetrics:
    def test_file_metrics_creation(self):
        from app.processors.codebase_analyzer import FileMetrics

        metrics = FileMetrics(path="test.py", language="python")
        assert metrics.path == "test.py"
        assert metrics.language == "python"
        assert metrics.lines_of_code == 0

    def test_file_metrics_to_dict(self):
        from app.processors.codebase_analyzer import FileMetrics

        metrics = FileMetrics(path="test.py", language="python", lines_of_code=100)
        result = metrics.to_dict()
        assert isinstance(result, dict)
        assert result["path"] == "test.py"
        assert result["lines_of_code"] == 100


class TestCodeMetrics:
    def test_code_metrics_creation(self):
        from app.processors.codebase_analyzer import CodeMetrics

        metrics = CodeMetrics()
        assert metrics.total_files == 0
        assert metrics.total_functions == 0

    def test_code_metrics_to_dict(self):
        from app.processors.codebase_analyzer import CodeMetrics

        metrics = CodeMetrics(total_files=5, total_functions=20)
        result = metrics.to_dict()
        assert isinstance(result, dict)
        assert result["total_files"] == 5
        assert result["total_functions"] == 20


class TestLanguageDetection:
    def test_detect_python(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("test.py") == "python"

    def test_detect_javascript(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("test.js") == "javascript"

    def test_detect_typescript(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("test.ts") == "typescript"

    def test_detect_tsx(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("test.tsx") == "tsx"

    def test_detect_go(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("main.go") == "go"

    def test_detect_ruby(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("app.rb") == "ruby"

    def test_detect_kotlin(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("Main.kt") == "kotlin"

    def test_detect_swift(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("App.swift") == "swift"

    def test_detect_dart(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("main.dart") == "dart"

    def test_detect_unknown(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        assert analyzer._detect_language("file.xyz") == "unknown"


class TestPythonAnalysis:
    def test_analyze_simple_python_file(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        content = """
def hello():
    print("Hello")

def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
        metrics = analyzer.analyze_file(content, "test.py")
        assert metrics.language == "python"
        assert metrics.lines_of_code > 0
        assert len(metrics.functions) >= 2

    def test_analyze_python_with_comments(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        content = """
# This is a comment
def hello():
    # Another comment
    print("Hello")
"""
        metrics = analyzer.analyze_file(content, "test.py")
        assert metrics.lines_of_comments >= 1


class TestJavaScriptAnalysis:
    def test_analyze_simple_js_file(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        content = """
function hello() {
    console.log("Hello");
}

const add = (a, b) => a + b;

class Calculator {
    multiply(x, y) {
        return x * y;
    }
}
"""
        metrics = analyzer.analyze_file(content, "test.js")
        assert metrics.language == "javascript"
        assert metrics.lines_of_code > 0


class TestAnalyzeFiles:
    def test_analyze_multiple_files(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        files = [
            {"path": "main.py", "content": "def main(): pass"},
            {"path": "utils.py", "content": "def helper(): pass"},
        ]
        metrics = analyzer.analyze_files(files)
        assert metrics.total_files == 2

    def test_analyze_empty_list(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        metrics = analyzer.analyze_files([])
        assert metrics.total_files == 0

    def test_graceful_skip_unknown_language(self):
        from app.processors.codebase_analyzer import CodebaseAnalyzer

        analyzer = CodebaseAnalyzer()
        files = [
            {"path": "data.csv", "content": "a,b,c\n1,2,3"},
        ]
        metrics = analyzer.analyze_files(files)
        assert metrics.total_files == 0
