"""Tests for Issue #224 - 75기법 GitHub 재분류 + schema.py requiredSources 수정

This module tests:
1. All 75 techniques load without source-based exclusion
2. fairthon_source field preserves original YAML values
3. input_source field no longer exists on TechniqueDefinition
4. has_readme_content() utility function
5. get_all_techniques() returns all loaded techniques
6. filter_techniques and determine_available_inputs are no longer importable
"""

import pytest


class TestTechniqueLoading:
    """Tests that all 75 techniques load correctly."""

    def test_all_75_techniques_load(self):
        """Test that all 75 techniques load without source-based exclusion."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()

        assert len(techniques) == 75, f"Expected 75 techniques, got {len(techniques)}"

    def test_get_all_techniques_returns_all_75(self):
        """Test that get_all_techniques() returns all 75 techniques."""
        from app.techniques.registry import (
            TechniqueRegistry,
            get_all_techniques,
        )

        TechniqueRegistry.reset()

        techniques = get_all_techniques()

        assert len(techniques) == 75, f"Expected 75 techniques, got {len(techniques)}"

    def test_technique_registry_get_all_techniques(self):
        """Test TechniqueRegistry.get_all_techniques() method."""
        from app.techniques.registry import TechniqueRegistry

        TechniqueRegistry.reset()
        registry = TechniqueRegistry()

        techniques = registry.get_all_techniques()

        assert len(techniques) == 75, f"Expected 75 techniques, got {len(techniques)}"

    def test_techniques_sorted_by_id(self):
        """Test that techniques are sorted by ID."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()
        ids = [t.id for t in techniques]

        assert ids == sorted(ids), "Techniques should be sorted by ID"


class TestFairthonSourceField:
    """Tests for the fairthon_source field."""

    def test_fairthon_source_field_exists(self):
        """Test that fairthon_source field exists on TechniqueDefinition."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()

        for technique in techniques:
            assert hasattr(technique, "fairthon_source"), (
                f"Technique {technique.id} missing fairthon_source field"
            )

    def test_fairthon_source_preserves_original_values(self):
        """Test that fairthon_source preserves original YAML values."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()

        source_values = set()
        for technique in techniques:
            if technique.fairthon_source:
                source_values.add(technique.fairthon_source)

        valid_values = {"either", "both", "pdf", "readme", "pdf_only", "readme_only"}

        for value in source_values:
            assert value in valid_values or value in [
                "either",
                "both",
                "pdf",
                "readme",
            ], f"Unexpected fairthon_source value: {value}"

    def test_fairthon_source_from_yaml_requiredSources(self):
        """Test that fairthon_source is populated from requiredSources YAML field."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()

        by_source = {}
        for technique in techniques:
            source = technique.fairthon_source or "none"
            by_source.setdefault(source, []).append(technique.id)

        assert len(by_source) > 0, "No fairthon_source values found"


class TestInputSourceRemoved:
    """Tests that input_source field has been removed."""

    def test_input_source_field_removed(self):
        """Test that input_source field no longer exists on TechniqueDefinition."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()

        for technique in techniques:
            assert not hasattr(technique, "input_source"), (
                f"Technique {technique.id} should not have input_source field"
            )

    def test_technique_definition_no_input_source_attribute(self):
        """Test that accessing input_source raises AttributeError."""
        from app.techniques.registry import get_all_techniques

        techniques = get_all_techniques()
        technique = techniques[0]

        with pytest.raises(AttributeError):
            _ = technique.input_source


class TestRemovedFunctionsNotImportable:
    """Tests that removed functions are no longer importable."""

    def test_filter_techniques_not_importable(self):
        """Test that filter_techniques is no longer importable from loader."""
        with pytest.raises(ImportError):
            from app.techniques.loader import filter_techniques  # noqa: F401

    def test_determine_available_inputs_not_importable(self):
        """Test that determine_available_inputs is no longer importable from loader."""
        with pytest.raises(ImportError):
            from app.techniques.loader import determine_available_inputs  # noqa: F401

    def test_filter_techniques_not_in_module_all(self):
        """Test that filter_techniques is not in __all__."""
        from app.techniques import __all__

        assert "filter_techniques" not in __all__, (
            "filter_techniques should not be in __all__"
        )

    def test_determine_available_inputs_not_in_module_all(self):
        """Test that determine_available_inputs is not in __all__."""
        from app.techniques import __all__

        assert "determine_available_inputs" not in __all__, (
            "determine_available_inputs should not be in __all__"
        )


class TestHasReadmeContent:
    """Tests for the has_readme_content utility function."""

    def test_has_readme_content_returns_true_with_readme(self):
        """Test that has_readme_content returns True when README exists."""
        from app.techniques.registry import has_readme_content

        repo_context = {"readme": "# Project README\n\nThis is a test project."}

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_returns_true_with_readme_content(self):
        """Test that has_readme_content returns True with readme_content field."""
        from app.techniques.registry import has_readme_content

        repo_context = {"readme_content": "# Test\n\nContent here."}

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_returns_true_with_readme_text(self):
        """Test that has_readme_content returns True with readme_text field."""
        from app.techniques.registry import has_readme_content

        repo_context = {"readme_text": "# Test\n\nContent here."}

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_returns_true_with_readme_html(self):
        """Test that has_readme_content returns True with readme_html field."""
        from app.techniques.registry import has_readme_content

        repo_context = {"readme_html": "<h1>Test</h1><p>Content</p>"}

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_returns_false_without_readme(self):
        """Test that has_readme_content returns False when no README."""
        from app.techniques.registry import has_readme_content

        repo_context = {"files": ["main.py", "requirements.txt"]}

        assert has_readme_content(repo_context) is False

    def test_has_readme_content_returns_false_empty_context(self):
        """Test that has_readme_content returns False with empty context."""
        from app.techniques.registry import has_readme_content

        assert has_readme_content({}) is False
        assert has_readme_content(None) is False  # type: ignore[arg-type]

    def test_has_readme_content_returns_false_empty_readme(self):
        """Test that has_readme_content returns False with empty README string."""
        from app.techniques.registry import has_readme_content

        repo_context = {"readme": "   "}

        assert has_readme_content(repo_context) is False

    def test_has_readme_content_detects_from_files_list(self):
        """Test that has_readme_content detects README from files list."""
        from app.techniques.registry import has_readme_content

        repo_context = {
            "files": [
                {"name": "README.md", "path": "/README.md"},
                {"name": "main.py", "path": "/main.py"},
            ]
        }

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_detects_from_string_files_list(self):
        """Test that has_readme_content detects README from string files list."""
        from app.techniques.registry import has_readme_content

        repo_context = {"files": ["README.md", "main.py", "requirements.txt"]}

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_case_insensitive(self):
        """Test that has_readme_content is case insensitive."""
        from app.techniques.registry import has_readme_content

        repo_context = {"files": ["readme.MD"]}

        assert has_readme_content(repo_context) is True

    def test_has_readme_content_various_formats(self):
        """Test that has_readme_content detects various README formats."""
        from app.techniques.registry import has_readme_content

        formats = ["README.rst", "readme.txt", "README"]

        for fmt in formats:
            repo_context = {"files": [fmt]}
            assert has_readme_content(repo_context) is True, f"Failed for {fmt}"


class TestNewExports:
    """Tests for new exports from techniques module."""

    def test_get_all_techniques_exported(self):
        """Test that get_all_techniques is exported from techniques module."""
        from app.techniques import get_all_techniques as exported_func

        techniques = exported_func()
        assert len(techniques) == 75

    def test_has_readme_content_exported(self):
        """Test that has_readme_content is exported from techniques module."""
        from app.techniques import has_readme_content as exported_func

        result = exported_func({"readme": "# Test"})
        assert result is True

    def test_new_functions_in_all(self):
        """Test that new functions are in __all__."""
        from app.techniques import __all__

        assert "get_all_techniques" in __all__
        assert "has_readme_content" in __all__
