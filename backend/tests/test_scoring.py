"""Tests for the BMAD scoring aggregation module."""

import pytest

from app.criteria.scoring import (
    adjust_score_by_confidence,
    calculate_exclusion_normalized_score,
    apply_confidence_adjustment_to_scores,
    is_information_absent,
    ItemStatus,
    NEUTRAL_SCORE_RATIO,
)


class TestAdjustScoreByConfidence:
    """Tests for adjust_score_by_confidence function."""

    def test_high_confidence_returns_raw_score_unchanged(self):
        """HIGH confidence should return raw_score unchanged."""
        raw_score = 50.0
        max_score = 100.0
        result = adjust_score_by_confidence(raw_score, max_score, "high")
        assert result == raw_score

    def test_medium_confidence_returns_eighty_five_percent(self):
        """MEDIUM confidence should return raw_score * 0.85."""
        raw_score = 100.0
        max_score = 100.0
        result = adjust_score_by_confidence(raw_score, max_score, "medium")
        assert result == 85.0

    def test_low_confidence_weighted_toward_neutral(self):
        """LOW confidence should weight toward neutral score."""
        raw_score = 100.0
        max_score = 100.0
        result = adjust_score_by_confidence(raw_score, max_score, "low")
        # Expected: 0.3 * 100 + 0.7 * (100 * 0.5) = 30 + 35 = 65
        expected = 0.3 * raw_score + 0.7 * (max_score * NEUTRAL_SCORE_RATIO)
        assert result == expected
        assert result == 65.0

    def test_clamps_to_max_score(self):
        """Result should not exceed max_score."""
        raw_score = 150.0
        max_score = 100.0
        result = adjust_score_by_confidence(raw_score, max_score, "high")
        assert result == max_score

    def test_clamps_to_zero(self):
        """Result should not go below 0."""
        raw_score = -50.0
        max_score = 100.0
        result = adjust_score_by_confidence(raw_score, max_score, "medium")
        assert result == 0.0


class TestCalculateExclusionNormalizedScore:
    """Tests for calculate_exclusion_normalized_score function."""

    def test_all_seventeen_evaluated_returns_raw_percentage(self):
        """All 17 items evaluated should return exact percentage."""
        item_scores = {
            "A1": {"score": 7.0, "max_score": 7.0, "status": ItemStatus.EVALUATED},
            "A2": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "A3": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "A4": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "B1": {"score": 7.0, "max_score": 7.0, "status": ItemStatus.EVALUATED},
            "B2": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "B3": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "B4": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "C1": {"score": 7.0, "max_score": 7.0, "status": ItemStatus.EVALUATED},
            "C2": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "C3": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "C4": {"score": 5.0, "max_score": 5.0, "status": ItemStatus.EVALUATED},
            "C5": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "D1": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "D2": {"score": 5.0, "max_score": 5.0, "status": ItemStatus.EVALUATED},
            "D3": {"score": 5.0, "max_score": 5.0, "status": ItemStatus.EVALUATED},
            "D4": {"score": 4.0, "max_score": 4.0, "status": ItemStatus.EVALUATED},
        }
        result = calculate_exclusion_normalized_score(item_scores)

        assert result["raw_score"] == 100.0
        assert result["max_possible"] == 100.0
        assert result["normalized_score"] == 100.0
        assert result["coverage_rate"] == 1.0
        assert len(result["evaluated_items"]) == 17
        assert len(result["excluded_items"]) == 0

    def test_ten_of_seventeen_evaluated_correct_normalization(self):
        """10/17 items evaluated should normalize based on evaluated items only."""
        item_scores = {
            "A1": {"score": 7.0, "max_score": 7.0, "status": ItemStatus.EVALUATED},
            "A2": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "A3": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "A4": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "B1": {"score": 7.0, "max_score": 7.0, "status": ItemStatus.EVALUATED},
            "B2": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "B3": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "B4": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "C1": {"score": 7.0, "max_score": 7.0, "status": ItemStatus.EVALUATED},
            "C2": {"score": 6.0, "max_score": 6.0, "status": ItemStatus.EVALUATED},
            "C3": {"score": 0.0, "max_score": 6.0, "status": ItemStatus.EXCLUDED},
            "C4": {"score": 0.0, "max_score": 5.0, "status": ItemStatus.EXCLUDED},
            "C5": {"score": 0.0, "max_score": 6.0, "status": ItemStatus.EXCLUDED},
            "D1": {"score": 0.0, "max_score": 6.0, "status": ItemStatus.EXCLUDED},
            "D2": {"score": 0.0, "max_score": 5.0, "status": ItemStatus.EXCLUDED},
            "D3": {"score": 0.0, "max_score": 5.0, "status": ItemStatus.EXCLUDED},
            "D4": {"score": 0.0, "max_score": 4.0, "status": ItemStatus.EXCLUDED},
        }
        result = calculate_exclusion_normalized_score(item_scores)

        # 10 evaluated items, all maxed: raw_score = 63, max_possible = 63
        assert result["raw_score"] == 63.0
        assert result["max_possible"] == 63.0
        assert result["normalized_score"] == 100.0  # All evaluated items got max
        assert result["coverage_rate"] == 10 / 17
        assert len(result["evaluated_items"]) == 10
        assert len(result["excluded_items"]) == 7

    def test_zero_items_returns_zero_gracefully(self):
        """Empty dict should return 0 gracefully without error."""
        item_scores = {}
        result = calculate_exclusion_normalized_score(item_scores)

        assert result["raw_score"] == 0.0
        assert result["max_possible"] == 0.0
        assert result["normalized_score"] == 0.0
        assert result["coverage_rate"] == 0.0
        assert len(result["evaluated_items"]) == 0
        assert len(result["excluded_items"]) == 0
        assert "0/17" in result["summary"]


class TestApplyConfidenceAdjustmentToScores:
    """Tests for apply_confidence_adjustment_to_scores function."""

    def test_replaces_scores_correctly(self):
        """Should apply confidence adjustment and return new dict."""
        # Use realistic scores that don't exceed BMAD max scores
        item_scores = {
            "A1": {
                "score": 5.0,
                "max_score": 7.0,
                "confidence": "medium",
                "status": ItemStatus.EVALUATED,
            },
            "A2": {
                "score": 6.0,
                "max_score": 6.0,
                "confidence": "high",
                "status": ItemStatus.EVALUATED,
            },
            "A3": {
                "score": 6.0,
                "max_score": 6.0,
                "confidence": "low",
                "status": ItemStatus.EVALUATED,
            },
        }
        result = apply_confidence_adjustment_to_scores(item_scores)

        # A1: medium confidence -> 5.0 * 0.85 = 4.25
        assert result["A1"]["score"] == pytest.approx(4.25)
        # A2: high confidence -> 6.0 * 1.0 = 6.0
        assert result["A2"]["score"] == 6.0
        # A3: low confidence -> 0.3 * 6.0 + 0.7 * 3.0 = 1.8 + 2.1 = 3.9
        assert result["A3"]["score"] == pytest.approx(3.9)

        # Original should not be mutated
        assert item_scores["A1"]["score"] == 5.0

    def test_skips_non_evaluated_items(self):
        """Should not adjust scores for excluded or missing items."""
        item_scores = {
            "A1": {
                "score": 50.0,
                "confidence": "medium",
                "status": ItemStatus.EXCLUDED,
            },
            "A2": {
                "score": 50.0,
                "confidence": "high",
                "status": ItemStatus.DATA_MISSING,
            },
        }
        result = apply_confidence_adjustment_to_scores(item_scores)

        # Scores should remain unchanged for non-evaluated items
        assert result["A1"]["score"] == 50.0
        assert result["A2"]["score"] == 50.0


class TestIsInformationAbsent:
    """Tests for is_information_absent function."""

    def test_detects_none_evidence(self):
        """Should return True when evidence is None."""
        assert is_information_absent(None, "Some rationale") is True

    def test_detects_empty_evidence_list(self):
        """Should return True when evidence is empty list."""
        assert is_information_absent([], "Some rationale") is True

    def test_detects_absence_keywords_in_rationale(self):
        """Should detect absence keywords in rationale (case-insensitive)."""
        keywords = [
            "no information",
            "NOT FOUND",
            "Not Available",
            "Cannot Determine",
            "Insufficient Data",
            "No Evidence",
            "Unable to Assess",
            "Not Provided",
            "ABSENT",
            "Missing",
        ]
        for keyword in keywords:
            assert (
                is_information_absent(["evidence"], f"This is {keyword} here") is True
            )

    def test_returns_false_with_evidence_and_no_keywords(self):
        """Should return False when evidence exists and no absence keywords."""
        assert (
            is_information_absent(["file1.py", "file2.py"], "Good quality code found")
            is False
        )

    def test_returns_false_with_evidence_and_empty_rationale(self):
        """Should return False with evidence even if rationale is empty."""
        assert is_information_absent(["evidence"], "") is False
