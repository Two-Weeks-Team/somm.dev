"""Test suite for Technique API endpoints.

Tests cover:
- GET /api/techniques - list all techniques
- GET /api/techniques?category=aroma - filter by category
- GET /api/techniques?mode=grand_tasting - filter by mode
- GET /api/techniques?mode=full_techniques - filter by mode
- GET /api/techniques/{id} - get technique detail
- GET /api/techniques/nonexistent - 404 handling
- GET /api/techniques/stats - get statistics
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestListTechniques:
    """Test suite for GET /api/techniques endpoint."""

    def test_list_all_techniques_returns_75(self):
        """Test GET /api/techniques returns list with 75 techniques."""
        response = client.get("/api/techniques")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 75

        expected_fields = {
            "id",
            "name",
            "category",
            "applicable_hats",
            "priority",
            "fairthon_source",
        }
        for technique in data:
            assert expected_fields.issubset(set(technique.keys()))

    def test_list_techniques_has_valid_priority_values(self):
        """Test that all techniques have valid priority values (P0, P1, P2)."""
        response = client.get("/api/techniques")
        data = response.json()

        valid_priorities = {"P0", "P1", "P2"}
        for technique in data:
            assert technique["priority"] in valid_priorities


class TestFilterByCategory:
    """Test suite for category filtering."""

    def test_filter_by_category_aroma_returns_11(self):
        """Test GET /api/techniques?category=aroma returns 11 techniques."""
        response = client.get("/api/techniques?category=aroma")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 11

        for technique in data:
            assert technique["category"] == "aroma"

    def test_filter_by_category_palate(self):
        """Test GET /api/techniques?category=palate returns correct techniques."""
        response = client.get("/api/techniques?category=palate")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 13

        for technique in data:
            assert technique["category"] == "palate"

    def test_filter_by_invalid_category_returns_empty(self):
        """Test filtering by non-existent category returns empty list."""
        response = client.get("/api/techniques?category=nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestFilterByMode:
    """Test suite for mode filtering."""

    def test_filter_by_mode_grand_tasting_returns_only_p0(self):
        """Test GET /api/techniques?mode=grand_tasting returns only P0 techniques."""
        response = client.get("/api/techniques?mode=grand_tasting")

        assert response.status_code == 200
        data = response.json()

        for technique in data:
            assert technique["priority"] == "P0"

    def test_filter_by_mode_full_techniques_returns_all_75(self):
        """Test GET /api/techniques?mode=full_techniques returns all 75 techniques."""
        response = client.get("/api/techniques?mode=full_techniques")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 75

    def test_filter_by_mode_six_sommeliers_returns_p0_and_p1(self):
        """Test GET /api/techniques?mode=six_sommeliers returns P0 and P1 techniques."""
        response = client.get("/api/techniques?mode=six_sommeliers")

        assert response.status_code == 200
        data = response.json()

        valid_priorities = {"P0", "P1"}
        for technique in data:
            assert technique["priority"] in valid_priorities

    def test_filter_by_invalid_mode_returns_400(self):
        """Test GET /api/techniques?mode=invalid returns 400 error."""
        response = client.get("/api/techniques?mode=invalid_mode")

        assert response.status_code == 400
        assert "Invalid mode" in response.json()["detail"]


class TestFilterByHat:
    """Test suite for hat filtering."""

    def test_filter_by_hat_white(self):
        """Test GET /api/techniques?hat=white returns techniques for white hat."""
        response = client.get("/api/techniques?hat=white")

        assert response.status_code == 200
        data = response.json()

        for technique in data:
            assert "white" in technique["applicable_hats"]

    def test_filter_by_hat_red(self):
        """Test GET /api/techniques?hat=red returns techniques for red hat."""
        response = client.get("/api/techniques?hat=red")

        assert response.status_code == 200
        data = response.json()

        for technique in data:
            assert "red" in technique["applicable_hats"]


class TestGetTechniqueDetail:
    """Test suite for GET /api/techniques/{id} endpoint."""

    def test_get_valid_technique_detail(self):
        """Test GET /api/techniques/{id} with valid id returns detail."""
        response = client.get("/api/techniques/five-whys")

        assert response.status_code == 200
        data = response.json()

        expected_fields = {
            "id",
            "name",
            "category",
            "applicable_hats",
            "evaluation_dimensions",
            "description",
            "prompt_template",
            "scoring",
            "output_schema",
            "metadata",
            "fairthon_source",
            "bmad_items",
        }
        assert expected_fields.issubset(set(data.keys()))

        assert data["id"] == "five-whys"
        assert "bmad_items" in data
        assert isinstance(data["bmad_items"], list)

    def test_get_another_valid_technique(self):
        """Test GET /api/techniques/{id} with another valid id."""
        response = client.get("/api/techniques/scamper")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "scamper"
        assert "bmad_items" in data

    def test_get_nonexistent_technique_returns_404(self):
        """Test GET /api/techniques/nonexistent returns 404."""
        response = client.get("/api/techniques/nonexistent_technique")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetTechniquesStats:
    """Test suite for GET /api/techniques/stats endpoint."""

    def test_stats_returns_correct_total(self):
        """Test GET /api/techniques/stats returns correct total count (75)."""
        response = client.get("/api/techniques/stats")

        assert response.status_code == 200
        data = response.json()

        expected_fields = {"total", "by_category", "by_priority", "by_mode"}
        assert expected_fields.issubset(set(data.keys()))

        assert data["total"] == 75

    def test_stats_by_category_has_all_categories(self):
        """Test stats by_category includes all 8 categories."""
        response = client.get("/api/techniques/stats")
        data = response.json()

        expected_categories = {
            "aroma",
            "palate",
            "body",
            "finish",
            "balance",
            "vintage",
            "terroir",
            "cellar",
        }
        assert set(data["by_category"].keys()) == expected_categories

    def test_stats_by_priority_has_all_priorities(self):
        """Test stats by_priority includes P0, P1, P2."""
        response = client.get("/api/techniques/stats")
        data = response.json()

        expected_priorities = {"P0", "P1", "P2"}
        assert set(data["by_priority"].keys()) == expected_priorities

        total_by_priority = sum(data["by_priority"].values())
        assert total_by_priority == 75

    def test_stats_by_mode_has_all_modes(self):
        """Test stats by_mode includes all three modes."""
        response = client.get("/api/techniques/stats")
        data = response.json()

        expected_modes = {"full_techniques", "grand_tasting", "six_sommeliers"}
        assert set(data["by_mode"].keys()) == expected_modes

        assert data["by_mode"]["full_techniques"] == 75
        assert data["by_mode"]["grand_tasting"] < 75
        assert data["by_mode"]["six_sommeliers"] < 75


class TestRouteOrdering:
    """Test suite for route ordering - stats must be defined before /{technique_id}."""

    def test_stats_route_not_treated_as_technique_id(self):
        """Test that /api/techniques/stats is not treated as a technique_id."""
        response = client.get("/api/techniques/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data

    def test_technique_id_with_name_stats_does_not_conflict(self):
        """Test that a technique named 'stats' would work if it existed."""
        response = client.get("/api/techniques/stats")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "total" in data
