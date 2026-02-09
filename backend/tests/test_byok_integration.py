"""Tests for BYOK (Bring Your Own Key) integration with evaluation pipeline.

These tests validate that stored API keys are correctly retrieved and used
in the evaluation pipeline with proper priority ordering.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestGetStoredKey:
    """Test suite for _get_stored_key helper function."""

    @pytest.mark.asyncio
    async def test_no_user_id_returns_none(self):
        """Test that empty user_id returns None key and 'none' source."""
        from app.services.evaluation_service import _get_stored_key

        key, source = await _get_stored_key("")
        assert key is None
        assert source == "none"

    @pytest.mark.asyncio
    async def test_with_stored_key_returns_decrypted(self):
        """Test that stored key is retrieved and decrypted correctly."""
        from app.services.evaluation_service import _get_stored_key

        mock_key_doc = {
            "encrypted_key": "encrypted-data-json",
            "key_hint": "...1234",
        }

        with (
            patch("app.database.repositories.api_key.APIKeyRepository") as MockRepo,
            patch("app.services.encryption.EncryptionService") as MockEncryption,
        ):
            mock_repo = MagicMock()
            mock_repo.get_key = AsyncMock(return_value=mock_key_doc)
            MockRepo.return_value = mock_repo

            mock_encryption = MagicMock()
            mock_encryption.decrypt.return_value = "decrypted-api-key"
            MockEncryption.return_value = mock_encryption

            key, source = await _get_stored_key("user-123", "google")

            assert key == "decrypted-api-key"
            assert source == "stored_byok"
            mock_repo.get_key.assert_called_once_with("user-123", "google")
            mock_encryption.decrypt.assert_called_once_with("encrypted-data-json")

    @pytest.mark.asyncio
    async def test_no_stored_key_returns_none(self):
        """Test that no stored key returns None key and 'none' source."""
        from app.services.evaluation_service import _get_stored_key

        with patch("app.database.repositories.api_key.APIKeyRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.get_key = AsyncMock(return_value=None)
            MockRepo.return_value = mock_repo

            key, source = await _get_stored_key("user-123", "google")

            assert key is None
            assert source == "none"
            mock_repo.get_key.assert_called_once_with("user-123", "google")

    @pytest.mark.asyncio
    async def test_exception_returns_none(self):
        """Test that exceptions are handled gracefully."""
        from app.services.evaluation_service import _get_stored_key

        with patch("app.database.repositories.api_key.APIKeyRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.get_key = AsyncMock(side_effect=Exception("DB error"))
            MockRepo.return_value = mock_repo

            key, source = await _get_stored_key("user-123", "google")

            assert key is None
            assert source == "none"


class TestKeyPriority:
    """Test suite for API key priority in _prepare_repo_context."""

    @pytest.mark.asyncio
    async def test_request_key_takes_priority(self):
        """When api_key is provided, stored key should NOT be looked up."""
        from app.services.evaluation_service import _prepare_repo_context

        with (
            patch("app.services.evaluation_service.parse_github_url") as mock_parse,
            patch("app.services.evaluation_service.GitHubService") as MockGitHub,
            patch("app.services.evaluation_service.load_techniques") as mock_load,
            patch("app.services.evaluation_service.resolve_byok") as mock_resolve,
            patch("app.services.evaluation_service._get_stored_key") as mock_get_stored,
        ):
            mock_parse.return_value = ("owner", "repo")

            mock_github = MagicMock()
            mock_github.get_full_repo_context = AsyncMock(
                return_value={"files": [], "tree": []}
            )
            MockGitHub.return_value = mock_github

            mock_load.return_value = ([], [])
            mock_resolve.return_value = ("resolved-key", None)

            repo_context, resolved_key = await _prepare_repo_context(
                repo_url="https://github.com/owner/repo",
                api_key="request-api-key",
                github_token=None,
                user_id="user-123",
            )

            mock_get_stored.assert_not_called()
            mock_resolve.assert_called_once_with("request-api-key")
            assert repo_context["api_key_source"] == "request_byok"
            assert resolved_key == "resolved-key"

    @pytest.mark.asyncio
    async def test_stored_key_used_when_no_request_key(self):
        """When api_key is None, stored key should be used."""
        from app.services.evaluation_service import _prepare_repo_context

        with (
            patch("app.services.evaluation_service.parse_github_url") as mock_parse,
            patch("app.services.evaluation_service.GitHubService") as MockGitHub,
            patch("app.services.evaluation_service.load_techniques") as mock_load,
            patch("app.services.evaluation_service.resolve_byok") as mock_resolve,
            patch("app.services.evaluation_service._get_stored_key") as mock_get_stored,
        ):
            mock_parse.return_value = ("owner", "repo")

            mock_github = MagicMock()
            mock_github.get_full_repo_context = AsyncMock(
                return_value={"files": [], "tree": []}
            )
            MockGitHub.return_value = mock_github

            mock_load.return_value = ([], [])
            mock_get_stored.return_value = ("stored-api-key", "stored_byok")
            mock_resolve.return_value = ("resolved-stored-key", None)

            repo_context, resolved_key = await _prepare_repo_context(
                repo_url="https://github.com/owner/repo",
                api_key=None,
                github_token=None,
                user_id="user-123",
            )

            mock_get_stored.assert_called_once_with("user-123")
            mock_resolve.assert_called_once_with("stored-api-key")
            assert repo_context["api_key_source"] == "stored_byok"
            assert resolved_key == "resolved-stored-key"

    @pytest.mark.asyncio
    async def test_system_default_when_no_keys(self):
        """When both api_key and stored key are None, use system default."""
        from app.services.evaluation_service import _prepare_repo_context

        with (
            patch("app.services.evaluation_service.parse_github_url") as mock_parse,
            patch("app.services.evaluation_service.GitHubService") as MockGitHub,
            patch("app.services.evaluation_service.load_techniques") as mock_load,
            patch("app.services.evaluation_service.resolve_byok") as mock_resolve,
            patch("app.services.evaluation_service._get_stored_key") as mock_get_stored,
        ):
            mock_parse.return_value = ("owner", "repo")

            mock_github = MagicMock()
            mock_github.get_full_repo_context = AsyncMock(
                return_value={"files": [], "tree": []}
            )
            MockGitHub.return_value = mock_github

            mock_load.return_value = ([], [])
            mock_get_stored.return_value = (None, "none")
            mock_resolve.return_value = (None, None)

            repo_context, resolved_key = await _prepare_repo_context(
                repo_url="https://github.com/owner/repo",
                api_key=None,
                github_token=None,
                user_id="user-123",
            )

            mock_get_stored.assert_called_once_with("user-123")
            mock_resolve.assert_called_once_with(None)
            assert repo_context["api_key_source"] == "system"
            assert resolved_key is None

    @pytest.mark.asyncio
    async def test_no_user_id_skips_stored_key_lookup(self):
        """When user_id is None, skip stored key lookup."""
        from app.services.evaluation_service import _prepare_repo_context

        with (
            patch("app.services.evaluation_service.parse_github_url") as mock_parse,
            patch("app.services.evaluation_service.GitHubService") as MockGitHub,
            patch("app.services.evaluation_service.load_techniques") as mock_load,
            patch("app.services.evaluation_service.resolve_byok") as mock_resolve,
            patch("app.services.evaluation_service._get_stored_key") as mock_get_stored,
        ):
            mock_parse.return_value = ("owner", "repo")

            mock_github = MagicMock()
            mock_github.get_full_repo_context = AsyncMock(
                return_value={"files": [], "tree": []}
            )
            MockGitHub.return_value = mock_github

            mock_load.return_value = ([], [])
            mock_resolve.return_value = (None, None)

            repo_context, resolved_key = await _prepare_repo_context(
                repo_url="https://github.com/owner/repo",
                api_key=None,
                github_token=None,
                user_id=None,
            )

            mock_get_stored.assert_not_called()
            mock_resolve.assert_called_once_with(None)
            assert repo_context["api_key_source"] == "system"


class TestByokErrorHandling:
    """Test suite for BYOK error handling in _prepare_repo_context."""

    @pytest.mark.asyncio
    async def test_byok_error_added_to_context(self):
        """Test that BYOK validation errors are added to repo_context."""
        from app.services.evaluation_service import _prepare_repo_context
        from app.providers.llm import BYOKValidationError

        with (
            patch("app.services.evaluation_service.parse_github_url") as mock_parse,
            patch("app.services.evaluation_service.GitHubService") as MockGitHub,
            patch("app.services.evaluation_service.load_techniques") as mock_load,
            patch("app.services.evaluation_service.resolve_byok") as mock_resolve,
        ):
            mock_parse.return_value = ("owner", "repo")

            mock_github = MagicMock()
            mock_github.get_full_repo_context = AsyncMock(
                return_value={"files": [], "tree": []}
            )
            MockGitHub.return_value = mock_github

            mock_load.return_value = ([], [])

            error = BYOKValidationError(
                error_code="invalid_api_key",
                message="API key is empty",
            )
            mock_resolve.return_value = (None, error)

            repo_context, resolved_key = await _prepare_repo_context(
                repo_url="https://github.com/owner/repo",
                api_key="",
                github_token=None,
                user_id=None,
            )

            assert "byok_error" in repo_context
            assert repo_context["byok_error"] == error
