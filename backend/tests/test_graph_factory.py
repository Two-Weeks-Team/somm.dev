import pytest

from app.graph.graph_factory import (
    EvaluationMode,
    InvalidEvaluationModeError,
    get_evaluation_graph,
    list_available_modes,
    is_valid_mode,
    _graph_builders,
)


@pytest.fixture(autouse=True)
def reset_graph_builders():
    _graph_builders.clear()
    yield
    _graph_builders.clear()


class TestEvaluationMode:
    def test_six_sommeliers_value(self):
        assert EvaluationMode.SIX_SOMMELIERS.value == "six_sommeliers"

    def test_grand_tasting_value(self):
        assert EvaluationMode.GRAND_TASTING.value == "grand_tasting"

    def test_full_techniques_value(self):
        assert EvaluationMode.FULL_TECHNIQUES.value == "full_techniques"


class TestListAvailableModes:
    def test_returns_both_modes(self):
        modes = list_available_modes()
        assert "six_sommeliers" in modes
        assert "grand_tasting" in modes
        assert len(modes) == 2


class TestIsValidMode:
    def test_six_sommeliers_valid(self):
        assert is_valid_mode("six_sommeliers") is True

    def test_grand_tasting_valid(self):
        assert is_valid_mode("grand_tasting") is True

    def test_invalid_mode_returns_false(self):
        assert is_valid_mode("invalid_mode") is False


class TestGetEvaluationGraph:
    def test_invalid_mode_raises_error(self):
        with pytest.raises(InvalidEvaluationModeError) as exc_info:
            get_evaluation_graph("invalid_mode")
        assert "invalid_mode" in str(exc_info.value)
        assert "Available modes" in str(exc_info.value)


class TestInvalidEvaluationModeError:
    def test_error_message_includes_mode(self):
        error = InvalidEvaluationModeError("bad_mode", ["mode1", "mode2"])
        assert "bad_mode" in str(error)

    def test_error_message_includes_available(self):
        error = InvalidEvaluationModeError("bad_mode", ["mode1", "mode2"])
        assert "mode1" in str(error)
        assert "mode2" in str(error)
