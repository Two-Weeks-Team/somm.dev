"""Tests for the quota checking service."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.quota import check_quota, QUOTA_RULES


class TestQuotaRules:
    """Tests for quota rules configuration."""

    def test_free_tier_limits(self):
        """Test free tier has correct limits."""
        rules = QUOTA_RULES["free"]
        assert rules["six_sommeliers"] == 2
        assert rules["grand_tasting"] == 2
        assert rules["full_techniques"] == 0

    def test_premium_tier_limits(self):
        """Test premium tier has correct limits."""
        rules = QUOTA_RULES["premium"]
        assert rules["six_sommeliers"] == 5
        assert rules["grand_tasting"] == 5
        assert rules["full_techniques"] == 5

    def test_pro_tier_limits(self):
        """Test pro tier has correct limits."""
        rules = QUOTA_RULES["pro"]
        assert rules["six_sommeliers"] == 5
        assert rules["grand_tasting"] == 5
        assert rules["full_techniques"] == 5

    def test_admin_unlimited(self):
        """Test admin tier has unlimited access."""
        rules = QUOTA_RULES["admin"]
        assert rules["six_sommeliers"] == -1
        assert rules["grand_tasting"] == -1
        assert rules["full_techniques"] == -1


@pytest.mark.asyncio
class TestCheckQuota:
    """Tests for the check_quota function."""

    async def test_admin_always_allowed(self):
        """Test admin users always pass quota check."""
        result = await check_quota("user1", "admin", "free", "six_sommeliers")
        assert result.allowed is True
        assert result.remaining == -1
        assert "Admin" in result.reason

    async def test_byok_always_allowed(self):
        """Test BYOK users always pass quota check."""
        result = await check_quota(
            "user1", "user", "free", "full_techniques", has_byok=True
        )
        assert result.allowed is True
        assert result.remaining == -1
        assert "BYOK" in result.reason

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=0,
    )
    async def test_free_tier_first_eval_allowed(self, mock_count):
        """Test free tier user can make first evaluation."""
        result = await check_quota("user1", "user", "free", "six_sommeliers")
        assert result.allowed is True
        assert result.remaining == 2
        assert result.daily_limit == 2
        assert result.used_today == 0

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=1,
    )
    async def test_free_tier_second_eval_allowed(self, mock_count):
        """Test free tier user can make second evaluation."""
        result = await check_quota("user1", "user", "free", "six_sommeliers")
        assert result.allowed is True
        assert result.remaining == 1
        assert result.used_today == 1

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=2,
    )
    async def test_free_tier_limit_reached(self, mock_count):
        """Test free tier user cannot exceed daily limit."""
        result = await check_quota("user1", "user", "free", "six_sommeliers")
        assert result.allowed is False
        assert result.remaining == 0
        assert "Daily limit" in result.reason
        assert result.suggestion is not None

    async def test_free_tier_full_techniques_requires_byok(self):
        """Test free tier cannot use full_techniques without BYOK."""
        result = await check_quota("user1", "user", "free", "full_techniques")
        assert result.allowed is False
        assert "BYOK" in result.reason
        assert (
            "upgrade" in result.suggestion.lower()
            or "plan" in result.suggestion.lower()
        )

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=0,
    )
    async def test_free_tier_full_techniques_with_byok(self, mock_count):
        """Test free tier can use full_techniques with BYOK."""
        result = await check_quota(
            "user1", "user", "free", "full_techniques", has_byok=True
        )
        assert result.allowed is True
        assert "BYOK" in result.reason

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=3,
    )
    async def test_premium_tier_within_limit(self, mock_count):
        """Test premium tier user within limit is allowed."""
        result = await check_quota("user1", "user", "premium", "six_sommeliers")
        assert result.allowed is True
        assert result.remaining == 2
        assert result.daily_limit == 5

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=5,
    )
    async def test_premium_tier_limit_reached(self, mock_count):
        """Test premium tier user cannot exceed daily limit."""
        result = await check_quota("user1", "user", "premium", "six_sommeliers")
        assert result.allowed is False
        assert "Daily limit" in result.reason

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=3,
    )
    async def test_pro_tier_within_limit(self, mock_count):
        """Test pro tier user within limit is allowed."""
        result = await check_quota("user1", "user", "pro", "grand_tasting")
        assert result.allowed is True
        assert result.remaining == 2

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=0,
    )
    async def test_unknown_plan_defaults_to_free(self, mock_count):
        """Test unknown plan defaults to free tier limits."""
        result = await check_quota("user1", "user", "unknown_plan", "six_sommeliers")
        assert result.allowed is True
        assert result.daily_limit == 2  # free tier limit

    @patch(
        "app.services.quota._count_today_evaluations",
        new_callable=AsyncMock,
        return_value=0,
    )
    async def test_unknown_mode_returns_zero_limit(self, mock_count):
        """Test unknown evaluation mode returns zero limit."""
        result = await check_quota("user1", "user", "free", "unknown_mode")
        assert result.allowed is False
        assert result.daily_limit == 0


class TestUserProperties:
    """Tests for User class properties related to quota."""

    def test_user_is_admin(self):
        """Test admin user properties."""
        from app.api.deps import User

        user = User(id="1", github_id="g1", username="admin", role="admin")
        assert user.is_admin is True
        assert user.is_paid is False
        assert user.is_free is True

    def test_user_is_paid_premium(self):
        """Test premium user properties."""
        from app.api.deps import User

        user = User(id="1", github_id="g1", username="premium", plan="premium")
        assert user.is_admin is False
        assert user.is_paid is True
        assert user.is_free is False

    def test_user_is_paid_pro(self):
        """Test pro user properties."""
        from app.api.deps import User

        user = User(id="1", github_id="g1", username="pro", plan="pro")
        assert user.is_admin is False
        assert user.is_paid is True
        assert user.is_free is False

    def test_user_default_free(self):
        """Test default user has free plan."""
        from app.api.deps import User

        user = User(id="1", github_id="g1", username="free")
        assert user.is_free is True
        assert user.role == "user"
        assert user.plan == "free"
        assert user.is_admin is False
        assert user.is_paid is False

    def test_user_explicit_role_and_plan(self):
        """Test user with explicit role and plan."""
        from app.api.deps import User

        user = User(
            id="1", github_id="g1", username="test", role="admin", plan="premium"
        )
        assert user.is_admin is True
        assert user.is_paid is True
        assert user.is_free is False
        assert user.role == "admin"
        assert user.plan == "premium"
