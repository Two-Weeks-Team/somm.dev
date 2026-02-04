# backend/tests/test_models_results.py
"""
Tests for Results models.
RED Phase: These tests should FAIL initially because the results model doesn't exist yet.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


class TestResultsModelImports:
    """Test that results models can be imported correctly"""

    def test_import_rating_tier_enum(self):
        """Test that RatingTier enum can be imported"""
        from app.models.results import RatingTier

        assert RatingTier is not None

    def test_import_sommelier_output(self):
        """Test that SommelierOutput can be imported"""
        from app.models.results import SommelierOutput

        assert SommelierOutput is not None

    def test_import_final_evaluation(self):
        """Test that FinalEvaluation can be imported"""
        from app.models.results import FinalEvaluation

        assert FinalEvaluation is not None

    def test_import_result_in_db(self):
        """Test that ResultInDB can be imported"""
        from app.models.results import ResultInDB

        assert ResultInDB is not None

    def test_import_result_response(self):
        """Test that ResultResponse can be imported"""
        from app.models.results import ResultResponse

        assert ResultResponse is not None

    def test_import_get_rating_tier_function(self):
        """Test that get_rating_tier function can be imported"""
        from app.models.results import get_rating_tier

        assert get_rating_tier is not None


class TestRatingTierEnum:
    """Test RatingTier enum values"""

    def test_rating_tier_has_legendary(self):
        """Test that RatingTier has 'Legendary' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "Legendary")

    def test_rating_tier_has_grand_cru(self):
        """Test that RatingTier has 'Grand Cru' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "Grand_Cru")

    def test_rating_tier_has_premier_cru(self):
        """Test that RatingTier has 'Premier Cru' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "Premier_Cru")

    def test_rating_tier_has_village(self):
        """Test that RatingTier has 'Village' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "Village")

    def test_rating_tier_has_table(self):
        """Test that RatingTier has 'Table' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "Table")

    def test_rating_tier_has_house_wine(self):
        """Test that RatingTier has 'House Wine' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "House_Wine")

    def test_rating_tier_has_corked(self):
        """Test that RatingTier has 'Corked' value"""
        from app.models.results import RatingTier

        assert hasattr(RatingTier, "Corked")


class TestGetRatingTierFunction:
    """Test get_rating_tier helper function"""

    def test_legendary_score_range(self):
        """Test get_rating_tier returns Legendary for scores 95-100"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(95) == RatingTier.Legendary
        assert get_rating_tier(97) == RatingTier.Legendary
        assert get_rating_tier(100) == RatingTier.Legendary

    def test_grand_cru_score_range(self):
        """Test get_rating_tier returns Grand Cru for scores 90-94"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(90) == RatingTier.Grand_Cru
        assert get_rating_tier(92) == RatingTier.Grand_Cru
        assert get_rating_tier(94) == RatingTier.Grand_Cru

    def test_premier_cru_score_range(self):
        """Test get_rating_tier returns Premier Cru for scores 85-89"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(85) == RatingTier.Premier_Cru
        assert get_rating_tier(87) == RatingTier.Premier_Cru
        assert get_rating_tier(89) == RatingTier.Premier_Cru

    def test_village_score_range(self):
        """Test get_rating_tier returns Village for scores 80-84"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(80) == RatingTier.Village
        assert get_rating_tier(82) == RatingTier.Village
        assert get_rating_tier(84) == RatingTier.Village

    def test_table_score_range(self):
        """Test get_rating_tier returns Table for scores 70-79"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(70) == RatingTier.Table
        assert get_rating_tier(75) == RatingTier.Table
        assert get_rating_tier(79) == RatingTier.Table

    def test_house_wine_score_range(self):
        """Test get_rating_tier returns House Wine for scores 60-69"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(60) == RatingTier.House_Wine
        assert get_rating_tier(65) == RatingTier.House_Wine
        assert get_rating_tier(69) == RatingTier.House_Wine

    def test_corked_score_range(self):
        """Test get_rating_tier returns Corked for scores below 60"""
        from app.models.results import RatingTier, get_rating_tier

        assert get_rating_tier(0) == RatingTier.Corked
        assert get_rating_tier(50) == RatingTier.Corked
        assert get_rating_tier(59) == RatingTier.Corked


class TestSommelierOutputModel:
    """Test SommelierOutput model"""

    def test_sommelier_output_has_sommelier_name(self):
        """Test that SommelierOutput has sommelier_name field"""
        from app.models.results import SommelierOutput

        assert "sommelier_name" in SommelierOutput.__fields__

    def test_sommelier_output_has_score(self):
        """Test that SommelierOutput has score field"""
        from app.models.results import SommelierOutput

        assert "score" in SommelierOutput.__fields__

    def test_sommelier_output_has_summary(self):
        """Test that SommelierOutput has summary field"""
        from app.models.results import SommelierOutput

        assert "summary" in SommelierOutput.__fields__

    def test_sommelier_output_has_recommendations(self):
        """Test that SommelierOutput has recommendations field"""
        from app.models.results import SommelierOutput

        assert "recommendations" in SommelierOutput.__fields__

    def test_sommelier_output_instance(self):
        """Test creating SommelierOutput instance"""
        from app.models.results import SommelierOutput

        output = SommelierOutput(
            sommelier_name="Marcel",
            score=85,
            summary="Well-structured codebase with good documentation.",
            recommendations=["Add more unit tests", "Consider using type hints"],
        )

        assert output.sommelier_name == "Marcel"
        assert output.score == 85
        assert len(output.recommendations) == 2


class TestFinalEvaluationModel:
    """Test FinalEvaluation model"""

    def test_final_evaluation_has_overall_score(self):
        """Test that FinalEvaluation has overall_score field"""
        from app.models.results import FinalEvaluation

        assert "overall_score" in FinalEvaluation.__fields__

    def test_final_evaluation_has_rating_tier(self):
        """Test that FinalEvaluation has rating_tier field"""
        from app.models.results import FinalEvaluation

        assert "rating_tier" in FinalEvaluation.__fields__

    def test_final_evaluation_has_sommelier_outputs(self):
        """Test that FinalEvaluation has sommelier_outputs field"""
        from app.models.results import FinalEvaluation

        assert "sommelier_outputs" in FinalEvaluation.__fields__

    def test_final_evaluation_has_summary(self):
        """Test that FinalEvaluation has summary field"""
        from app.models.results import FinalEvaluation

        assert "summary" in FinalEvaluation.__fields__

    def test_final_evaluation_instance(self):
        """Test creating FinalEvaluation instance"""
        from app.models.results import FinalEvaluation, RatingTier, SommelierOutput

        outputs = [
            SommelierOutput(
                sommelier_name="Marcel",
                score=85,
                summary="Good structure.",
                recommendations=[],
            ),
            SommelierOutput(
                sommelier_name="Isabella",
                score=90,
                summary="Excellent quality.",
                recommendations=[],
            ),
        ]

        eval = FinalEvaluation(
            overall_score=87,
            rating_tier=RatingTier.Premier_Cru,
            sommelier_outputs=outputs,
            summary="A well-crafted codebase with excellent quality standards.",
        )

        assert eval.overall_score == 87
        assert eval.rating_tier == RatingTier.Premier_Cru
        assert len(eval.sommelier_outputs) == 2


class TestResultInDBModel:
    """Test ResultInDB model"""

    def test_result_in_db_has_evaluation_id(self):
        """Test that ResultInDB has evaluation_id field"""
        from app.models.results import ResultInDB

        assert "evaluation_id" in ResultInDB.__fields__

    def test_result_in_db_has_final_evaluation(self):
        """Test that ResultInDB has final_evaluation field"""
        from app.models.results import ResultInDB

        assert "final_evaluation" in ResultInDB.__fields__

    def test_result_in_db_has_id(self):
        """Test that ResultInDB has id field"""
        from app.models.results import ResultInDB

        assert "id" in ResultInDB.__fields__

    def test_result_in_db_has_created_at(self):
        """Test that ResultInDB has created_at field"""
        from app.models.results import ResultInDB

        assert "created_at" in ResultInDB.__fields__


class TestResultResponseModel:
    """Test ResultResponse model"""

    def test_result_response_has_evaluation_id(self):
        """Test that ResultResponse has evaluation_id field"""
        from app.models.results import ResultResponse

        assert "evaluation_id" in ResultResponse.__fields__

    def test_result_response_has_final_evaluation(self):
        """Test that ResultResponse has final_evaluation field"""
        from app.models.results import ResultResponse

        assert "final_evaluation" in ResultResponse.__fields__

    def test_result_response_has_created_at(self):
        """Test that ResultResponse has created_at field"""
        from app.models.results import ResultResponse

        assert "created_at" in ResultResponse.__fields__
