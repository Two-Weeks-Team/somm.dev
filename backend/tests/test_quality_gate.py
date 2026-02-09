import pytest
from app.constants import (
    get_quality_gate,
    PASS_THRESHOLD,
    CONCERNS_THRESHOLD,
    COVERAGE_THRESHOLD,
)


class TestQualityGate:
    def test_pass_threshold_exact(self):
        result = get_quality_gate(70.0, 0.5)
        assert result == "PASS"

    def test_pass_threshold_high_coverage(self):
        result = get_quality_gate(100.0, 1.0)
        assert result == "PASS"

    def test_concerns_threshold_exact(self):
        result = get_quality_gate(50.0, 0.5)
        assert result == "CONCERNS"

    def test_concerns_between_thresholds(self):
        result = get_quality_gate(69.9, 0.5)
        assert result == "CONCERNS"

    def test_fail_below_concerns(self):
        result = get_quality_gate(49.9, 0.5)
        assert result == "FAIL"

    def test_fail_at_zero(self):
        result = get_quality_gate(0.0, 1.0)
        assert result == "FAIL"

    def test_incomplete_low_coverage(self):
        result = get_quality_gate(85.0, 0.3)
        assert result == "INCOMPLETE"

    def test_incomplete_boundary_low(self):
        result = get_quality_gate(85.0, 0.49)
        assert result == "INCOMPLETE"

    def test_pass_at_coverage_threshold(self):
        result = get_quality_gate(85.0, 0.5)
        assert result == "PASS"

    def test_constants_defined(self):
        assert PASS_THRESHOLD == 70
        assert CONCERNS_THRESHOLD == 50
        assert COVERAGE_THRESHOLD == 0.5
