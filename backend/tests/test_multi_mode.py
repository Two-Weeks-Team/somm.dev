"""Tests for multi-mode graph evaluation support."""

import pytest

from app.services.graph_registry import GraphRegistry


class TestGraphRegistry:
    def test_registry_clear(self):
        from app.services import graph_registry as _mod

        saved_2d = dict(_mod._builders_2d)
        saved_3d = dict(_mod._builders_3d)
        try:
            GraphRegistry.clear()
            assert GraphRegistry.supported_modes() == []
            assert not GraphRegistry.is_supported("test_mode")
        finally:
            _mod._builders_2d.update(saved_2d)
            _mod._builders_3d.update(saved_3d)

    def test_register_2d_builder(self):
        from app.services import graph_registry as _mod

        saved = dict(_mod._builders_2d)
        try:

            def mock_builder(evaluation_id: str):
                return {"evaluation_id": evaluation_id}

            GraphRegistry.register_2d("test_mode", mock_builder)

            assert GraphRegistry.is_supported("test_mode")
            assert "test_mode" in GraphRegistry.supported_modes()
        finally:
            _mod._builders_2d.clear()
            _mod._builders_2d.update(saved)

    def test_register_3d_builder(self):
        from app.services import graph_registry as _mod

        saved = dict(_mod._builders_3d)
        try:

            def mock_builder_3d(evaluation_id: str, techniques: list | None = None):
                return {"evaluation_id": evaluation_id}

            GraphRegistry.register_3d("test_mode_3d", mock_builder_3d)

            builder = GraphRegistry.get_3d_builder("test_mode_3d")
            assert builder == mock_builder_3d
        finally:
            _mod._builders_3d.clear()
            _mod._builders_3d.update(saved)

    def test_get_2d_builder_raises_for_unsupported_mode(self):
        with pytest.raises(ValueError, match="Unsupported mode: nonexistent"):
            GraphRegistry.get_2d_builder("nonexistent")

    def test_get_3d_builder_raises_for_unsupported_mode(self):
        with pytest.raises(ValueError, match="Unsupported mode: nonexistent"):
            GraphRegistry.get_3d_builder("nonexistent")

    def test_supported_modes_returns_list(self):
        modes = GraphRegistry.supported_modes()
        assert isinstance(modes, list)

    def test_is_supported_returns_false_for_unknown(self):
        assert GraphRegistry.is_supported("unknown_mode") is False

    def test_register_and_retrieve_2d(self):
        from app.services import graph_registry as _mod

        saved = dict(_mod._builders_2d)
        try:

            def builder(eval_id: str):
                return {"id": eval_id}

            GraphRegistry.register_2d("custom", builder)
            retrieved = GraphRegistry.get_2d_builder("custom")
            assert retrieved == builder
            result = retrieved("test_123")
            assert result == {"id": "test_123"}
        finally:
            _mod._builders_2d.clear()
            _mod._builders_2d.update(saved)

    def test_register_overwrites_existing(self):
        from app.services import graph_registry as _mod

        saved = dict(_mod._builders_2d)
        try:

            def builder1(eval_id: str):
                return {"version": 1}

            def builder2(eval_id: str):
                return {"version": 2}

            GraphRegistry.register_2d("overwrite_test", builder1)
            GraphRegistry.register_2d("overwrite_test", builder2)

            retrieved = GraphRegistry.get_2d_builder("overwrite_test")
            assert retrieved("x") == {"version": 2}
        finally:
            _mod._builders_2d.clear()
            _mod._builders_2d.update(saved)


class TestModeConstants:
    def test_six_sommeliers_constant(self):
        from app.graph.graph_factory import EvaluationMode

        assert EvaluationMode.SIX_SOMMELIERS.value == "six_sommeliers"

    def test_grand_tasting_constant(self):
        from app.graph.graph_factory import EvaluationMode

        assert EvaluationMode.GRAND_TASTING.value == "grand_tasting"

    def test_full_techniques_constant(self):
        from app.graph.graph_factory import EvaluationMode

        assert EvaluationMode.FULL_TECHNIQUES.value == "full_techniques"

    def test_evaluation_mode_is_string_enum(self):
        from app.graph.graph_factory import EvaluationMode

        assert isinstance(EvaluationMode.SIX_SOMMELIERS.value, str)
        assert isinstance(EvaluationMode.GRAND_TASTING.value, str)
        assert isinstance(EvaluationMode.FULL_TECHNIQUES.value, str)

    def test_old_six_hats_value_rejected(self):
        """Test that old 'six_hats' value is rejected."""
        from app.graph.graph_factory import EvaluationMode
        import pytest

        with pytest.raises(ValueError):
            EvaluationMode("six_hats")
