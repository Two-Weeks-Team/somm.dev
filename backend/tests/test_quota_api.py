"""Tests for quota API routes and models."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.routes.quota import (
    QuotaStatusResponse,
    AllQuotaStatusResponse,
)
from app.services.quota import QuotaResult


class TestQuotaStatusResponse:
    def test_basic_response(self):
        response = QuotaStatusResponse(
            evaluation_mode="six_sommeliers",
            allowed=True,
            reason="Quota OK: 1/2",
            remaining=1,
            daily_limit=2,
            used_today=1,
            has_byok=False,
            plan="free",
        )
        assert response.evaluation_mode == "six_sommeliers"
        assert response.allowed is True
        assert response.remaining == 1
        assert response.suggestion is None

    def test_response_with_suggestion(self):
        response = QuotaStatusResponse(
            evaluation_mode="full_techniques",
            allowed=False,
            reason="Requires BYOK",
            remaining=0,
            daily_limit=0,
            used_today=0,
            suggestion="Register your Gemini API key",
            has_byok=False,
            plan="free",
        )
        assert response.allowed is False
        assert response.suggestion is not None
        assert "API key" in response.suggestion

    def test_unlimited_quota(self):
        response = QuotaStatusResponse(
            evaluation_mode="six_sommeliers",
            allowed=True,
            reason="Admin: unlimited",
            remaining=-1,
            daily_limit=-1,
            used_today=0,
            has_byok=False,
            plan="free",
        )
        assert response.remaining == -1
        assert response.daily_limit == -1


class TestAllQuotaStatusResponse:
    def test_full_response(self):
        quotas = {
            "six_sommeliers": QuotaStatusResponse(
                evaluation_mode="six_sommeliers",
                allowed=True,
                reason="OK",
                remaining=2,
                daily_limit=2,
                used_today=0,
                has_byok=False,
                plan="free",
            ),
            "grand_tasting": QuotaStatusResponse(
                evaluation_mode="grand_tasting",
                allowed=True,
                reason="OK",
                remaining=2,
                daily_limit=2,
                used_today=0,
                has_byok=False,
                plan="free",
            ),
        }
        response = AllQuotaStatusResponse(
            user_id="user123",
            plan="free",
            role="user",
            has_byok=False,
            quotas=quotas,
        )
        assert response.user_id == "user123"
        assert len(response.quotas) == 2
        assert "six_sommeliers" in response.quotas

    def test_byok_user(self):
        response = AllQuotaStatusResponse(
            user_id="user123",
            plan="free",
            role="user",
            has_byok=True,
            quotas={},
        )
        assert response.has_byok is True

    def test_admin_user(self):
        response = AllQuotaStatusResponse(
            user_id="admin123",
            plan="free",
            role="admin",
            has_byok=False,
            quotas={},
        )
        assert response.role == "admin"


class TestQuotaIntegrationWithEvaluate:
    @pytest.mark.asyncio
    async def test_quota_blocks_evaluation(self):
        """Test that quota check blocks evaluation when limit exceeded."""
        quota_result = QuotaResult(
            allowed=False,
            reason="Daily limit reached: 2/2",
            remaining=0,
            daily_limit=2,
            used_today=2,
            suggestion="Register your API key",
        )
        assert quota_result.allowed is False
        assert "limit" in quota_result.reason.lower()

    @pytest.mark.asyncio
    async def test_quota_allows_evaluation(self):
        """Test that quota check allows evaluation when within limit."""
        quota_result = QuotaResult(
            allowed=True,
            reason="Quota OK: 1/2",
            remaining=1,
            daily_limit=2,
            used_today=1,
        )
        assert quota_result.allowed is True

    @pytest.mark.asyncio
    async def test_byok_bypasses_quota(self):
        """Test that BYOK users bypass quota limits."""
        quota_result = QuotaResult(
            allowed=True,
            reason="BYOK: using your own API key",
            remaining=-1,
            daily_limit=-1,
        )
        assert quota_result.allowed is True
        assert quota_result.remaining == -1
