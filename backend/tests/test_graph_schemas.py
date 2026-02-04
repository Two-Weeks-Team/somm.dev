"""Tests for app/graph/schemas.py - SommelierOutput and FinalEvaluation schemas"""

import pytest
from pydantic import ValidationError
from app.graph.schemas import SommelierOutput, FinalEvaluation


class TestSommelierOutput:
    """Test cases for SommelierOutput schema"""

    def test_sommelier_output_valid_score(self):
        """Test that valid score values are accepted"""
        output = SommelierOutput(
            score=85,
            notes="A robust vintage with excellent structure",
            confidence=0.9,
            techniques_used=["static_analysis", "metric_extraction"],
            aspects={"readability": 8.5, "maintainability": 8.0},
        )
        assert output.score == 85
        assert output.confidence == 0.9

    def test_sommelier_output_min_score(self):
        """Test minimum score value (0)"""
        output = SommelierOutput(
            score=0,
            notes="A challenging vintage",
            confidence=0.1,
            techniques_used=["static_analysis"],
            aspects={},
        )
        assert output.score == 0

    def test_sommelier_output_max_score(self):
        """Test maximum score value (100)"""
        output = SommelierOutput(
            score=100,
            notes="An exceptional vintage",
            confidence=1.0,
            techniques_used=[
                "static_analysis",
                "metric_extraction",
                "semantic_analysis",
            ],
            aspects={"readability": 10.0, "maintainability": 10.0},
        )
        assert output.score == 100

    def test_sommelier_output_score_below_min(self):
        """Test that score below 0 raises ValidationError"""
        with pytest.raises(ValidationError):
            SommelierOutput(
                score=-1,
                notes="Invalid score",
                confidence=0.5,
                techniques_used=[],
                aspects={},
            )

    def test_sommelier_output_score_above_max(self):
        """Test that score above 100 raises ValidationError"""
        with pytest.raises(ValidationError):
            SommelierOutput(
                score=101,
                notes="Invalid score",
                confidence=0.5,
                techniques_used=[],
                aspects={},
            )

    def test_sommelier_output_confidence_below_min(self):
        """Test that confidence below 0.0 raises ValidationError"""
        with pytest.raises(ValidationError):
            SommelierOutput(
                score=75,
                notes="Invalid confidence",
                confidence=-0.1,
                techniques_used=[],
                aspects={},
            )

    def test_sommelier_output_confidence_above_max(self):
        """Test that confidence above 1.0 raises ValidationError"""
        with pytest.raises(ValidationError):
            SommelierOutput(
                score=75,
                notes="Invalid confidence",
                confidence=1.1,
                techniques_used=[],
                aspects={},
            )

    def test_sommelier_output_default_techniques(self):
        """Test that techniques_used defaults to empty list"""
        output = SommelierOutput(
            score=75, notes="Default techniques", confidence=0.5, aspects={}
        )
        assert output.techniques_used == []

    def test_sommelier_output_default_aspects(self):
        """Test that aspects defaults to empty dict"""
        output = SommelierOutput(
            score=75, notes="Default aspects", confidence=0.5, techniques_used=[]
        )
        assert output.aspects == {}

    def test_sommelier_output_notes_wine_metaphor(self):
        """Test that notes can contain wine metaphor style descriptions"""
        output = SommelierOutput(
            score=92,
            notes="This vintage presents notes of oak and tannin structure with a finish that speaks to careful aging potential",
            confidence=0.95,
            techniques_used=["nose_analysis", "taste_profile"],
            aspects={"complexity": 9.2, "balance": 9.5},
        )
        assert "oak" in output.notes
        assert "tannin" in output.notes

    def test_sommelier_output_dict_method(self):
        """Test that dict() method works correctly"""
        output = SommelierOutput(
            score=80,
            notes="Test notes",
            confidence=0.8,
            techniques_used=["technique1"],
            aspects={"key": "value"},
        )
        output_dict = output.dict()
        assert output_dict["score"] == 80
        assert output_dict["notes"] == "Test notes"
        assert output_dict["confidence"] == 0.8


class TestFinalEvaluation:
    """Test cases for FinalEvaluation schema"""

    def test_final_evaluation_valid_score(self):
        """Test that valid total_score values are accepted"""
        evaluation = FinalEvaluation(
            total_score=85,
            rating="Premier Cru",
            verdict="An excellent vintage with great potential",
            pairing_suggestions=["Roasted duck", "Aged cheese"],
            cellaring_advice="Store horizontally at 55°F for optimal aging",
            aspect_scores={"structure": 8.5, "aroma": 8.0, "finish": 8.5},
        )
        assert evaluation.total_score == 85
        assert evaluation.rating == "Premier Cru"

    def test_final_evaluation_min_score(self):
        """Test minimum total_score value (0)"""
        evaluation = FinalEvaluation(
            total_score=0,
            rating="Corked",
            verdict="Below expectations",
            pairing_suggestions=[],
            cellaring_advice="Consume immediately or discard",
            aspect_scores={},
        )
        assert evaluation.total_score == 0

    def test_final_evaluation_max_score(self):
        """Test maximum total_score value (100)"""
        evaluation = FinalEvaluation(
            total_score=100,
            rating="Legendary",
            verdict="A perfect vintage",
            pairing_suggestions=["Special occasion", "Solo enjoyment"],
            cellaring_advice="Cellar for 20+ years",
            aspect_scores={"complexity": 10.0, "balance": 10.0, "finish": 10.0},
        )
        assert evaluation.total_score == 100

    def test_final_evaluation_score_below_min(self):
        """Test that total_score below 0 raises ValidationError"""
        with pytest.raises(ValidationError):
            FinalEvaluation(
                total_score=-1,
                rating="Invalid",
                verdict="Invalid score",
                pairing_suggestions=[],
                cellaring_advice="",
                aspect_scores={},
            )

    def test_final_evaluation_score_above_max(self):
        """Test that total_score above 100 raises ValidationError"""
        with pytest.raises(ValidationError):
            FinalEvaluation(
                total_score=101,
                rating="Invalid",
                verdict="Invalid score",
                pairing_suggestions=[],
                cellaring_advice="",
                aspect_scores={},
            )

    def test_final_evaluation_default_pairing_suggestions(self):
        """Test that pairing_suggestions defaults to empty list"""
        evaluation = FinalEvaluation(
            total_score=75,
            rating="Village",
            verdict="A good wine",
            cellaring_advice="Drink within 2 years",
            aspect_scores={},
        )
        assert evaluation.pairing_suggestions == []

    def test_final_evaluation_default_aspect_scores(self):
        """Test that aspect_scores defaults to empty dict"""
        evaluation = FinalEvaluation(
            total_score=75,
            rating="Village",
            verdict="A good wine",
            pairing_suggestions=[],
            cellaring_advice="Drink within 2 years",
        )
        assert evaluation.aspect_scores == {}

    def test_final_evaluation_rating_tiers(self):
        """Test various rating tiers"""
        ratings = [
            (95, "Legendary"),
            (92, "Grand Cru"),
            (87, "Premier Cru"),
            (82, "Village"),
            (75, "Table"),
            (65, "House Wine"),
        ]
        for score, expected_rating in ratings:
            evaluation = FinalEvaluation(
                total_score=score,
                rating=expected_rating,
                verdict="Test verdict",
                pairing_suggestions=[],
                cellaring_advice="",
                aspect_scores={},
            )
            assert evaluation.rating == expected_rating

    def test_final_evaluation_cellaring_advice(self):
        """Test that cellaring_advice can contain maintenance recommendations"""
        evaluation = FinalEvaluation(
            total_score=88,
            rating="Premier Cru",
            verdict="Excellent potential",
            pairing_suggestions=["Duck confit", "Mushroom risotto"],
            cellaring_advice="Keep at consistent 55°F temperature, 70% humidity, away from light",
            aspect_scores={"structure": 9.0, "balance": 8.5},
        )
        assert "55°F" in evaluation.cellaring_advice
        assert "humidity" in evaluation.cellaring_advice

    def test_final_evaluation_dict_method(self):
        """Test that dict() method works correctly"""
        evaluation = FinalEvaluation(
            total_score=82,
            rating="Village",
            verdict="A solid wine",
            pairing_suggestions=["Pasta", "Pizza"],
            cellaring_advice="Drink soon",
            aspect_scores={"balance": 8.2},
        )
        eval_dict = evaluation.dict()
        assert eval_dict["total_score"] == 82
        assert eval_dict["rating"] == "Village"
        assert eval_dict["pairing_suggestions"] == ["Pasta", "Pizza"]


class TestSchemaValidation:
    """Integration tests for schema validation"""

    def test_sommelier_to_final_evaluation_flow(self):
        """Test that SommelierOutput can be used to build FinalEvaluation"""
        sommelier_results = [
            SommelierOutput(
                score=85,
                notes="Excellent structure",
                confidence=0.9,
                techniques_used=["analysis"],
                aspects={"readability": 8.5},
            ),
            SommelierOutput(
                score=78,
                notes="Good complexity",
                confidence=0.85,
                techniques_used=["review"],
                aspects={"maintainability": 7.8},
            ),
        ]

        avg_score = sum(r.score for r in sommelier_results) // len(sommelier_results)

        final_eval = FinalEvaluation(
            total_score=avg_score,
            rating="Village",
            verdict="A solid vintage",
            pairing_suggestions=["Pasta with tomato sauce"],
            cellaring_advice="Consume within 3 years",
            aspect_scores={
                "readability": sommelier_results[0].aspects["readability"],
                "maintainability": sommelier_results[1].aspects["maintainability"],
            },
        )

        assert final_eval.total_score == 81
        assert final_eval.aspect_scores["readability"] == 8.5
        assert final_eval.aspect_scores["maintainability"] == 7.8
