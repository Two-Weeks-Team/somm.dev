"""Tests for the key validator service."""

from unittest import mock

import httpx
import pytest

from app.services.key_validator import validate_gemini_key, ValidationResult


class TestValidateGeminiKey:
    """Test suite for validate_gemini_key function."""

    @pytest.mark.asyncio
    async def test_valid_key_returns_true(self):
        """Test that a valid key returns valid=True with models."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "models/gemini-1.5-flash"},
                {"name": "models/gemini-1.5-pro"},
            ]
        }

        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(return_value=mock_response)

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("valid-api-key")

        assert result.valid is True
        assert result.error is None
        assert "models/gemini-1.5-flash" in result.models_available
        assert "models/gemini-1.5-pro" in result.models_available

    @pytest.mark.asyncio
    async def test_invalid_key_returns_false(self):
        """Test that an invalid key (401) returns valid=False."""
        mock_response = mock.Mock()
        mock_response.status_code = 401

        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(return_value=mock_response)

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("invalid-api-key")

        assert result.valid is False
        assert result.error == "Invalid API key"
        assert result.models_available == []

    @pytest.mark.asyncio
    async def test_forbidden_key_returns_false(self):
        """Test that a forbidden key (403) returns valid=False."""
        mock_response = mock.Mock()
        mock_response.status_code = 403

        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(return_value=mock_response)

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("forbidden-api-key")

        assert result.valid is False
        assert result.error == "Invalid API key"

    @pytest.mark.asyncio
    async def test_unexpected_status_returns_error(self):
        """Test that unexpected status codes return an error."""
        mock_response = mock.Mock()
        mock_response.status_code = 500

        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(return_value=mock_response)

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("some-key")

        assert result.valid is False
        assert "Unexpected status: 500" in result.error

    @pytest.mark.asyncio
    async def test_timeout_returns_error(self):
        """Test that timeout exception returns an error."""
        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("some-key")

        assert result.valid is False
        assert result.error == "Validation timed out"

    @pytest.mark.asyncio
    async def test_network_error_returns_error(self):
        """Test that network errors return an error."""
        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("some-key")

        assert result.valid is False
        assert "Network error" in result.error

    @pytest.mark.asyncio
    async def test_empty_models_list(self):
        """Test that empty models list is handled correctly."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}

        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(return_value=mock_response)

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("valid-key")

        assert result.valid is True
        assert result.models_available == []

    @pytest.mark.asyncio
    async def test_models_without_name(self):
        """Test that models without name field are handled gracefully."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "models/gemini-1.5-flash"},
                {"version": "1.0"},
            ]
        }

        mock_client = mock.AsyncMock()
        mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client.get = mock.AsyncMock(return_value=mock_response)

        with mock.patch("httpx.AsyncClient", return_value=mock_client):
            result = await validate_gemini_key("valid-key")

        assert result.valid is True
        assert "" in result.models_available
        assert "models/gemini-1.5-flash" in result.models_available

    @pytest.mark.asyncio
    async def test_validation_result_dataclass(self):
        """Test ValidationResult dataclass creation."""
        result = ValidationResult(valid=True, models_available=["model1", "model2"])
        assert result.valid is True
        assert result.error is None
        assert result.models_available == ["model1", "model2"]

    @pytest.mark.asyncio
    async def test_validation_result_with_error(self):
        """Test ValidationResult with error."""
        result = ValidationResult(valid=False, error="Test error")
        assert result.valid is False
        assert result.error == "Test error"
        assert result.models_available == []
