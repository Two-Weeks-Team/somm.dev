"""Tests for API key routes and models.

These tests validate the Pydantic models and service logic without
depending on the database or FastAPI TestClient.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.api.routes.api_keys import (
    RegisterKeyRequest,
    RegisterKeyResponse,
    KeyStatusResponse,
    ValidateKeyRequest,
    ValidateKeyResponse,
)
from app.services.encryption import EncryptionService
from app.services.key_validator import ValidationResult


class TestRegisterKeyRequest:
    """Test suite for RegisterKeyRequest model."""

    def test_valid_request(self):
        """Test that a valid request is created correctly."""
        request = RegisterKeyRequest(provider="google", api_key="test-key-123")
        assert request.provider == "google"
        assert request.api_key == "test-key-123"

    def test_default_provider(self):
        """Test that default provider is 'google'."""
        request = RegisterKeyRequest(api_key="test-key")
        assert request.provider == "google"

    def test_custom_provider(self):
        """Test that custom provider can be set."""
        request = RegisterKeyRequest(provider="openai", api_key="test-key")
        assert request.provider == "openai"


class TestRegisterKeyResponse:
    """Test suite for RegisterKeyResponse model."""

    def test_valid_response(self):
        """Test that a valid response is created correctly."""
        response = RegisterKeyResponse(
            valid=True, key_hint="...1234", provider="google"
        )
        assert response.valid is True
        assert response.key_hint == "...1234"
        assert response.provider == "google"
        assert response.expires_at is None

    def test_response_with_expiry(self):
        """Test response with expiration datetime."""
        expiry = datetime.now(timezone.utc)
        response = RegisterKeyResponse(
            valid=True,
            key_hint="...5678",
            provider="google",
            expires_at=expiry,
        )
        assert response.expires_at == expiry


class TestKeyStatusResponse:
    """Test suite for KeyStatusResponse model."""

    def test_valid_response(self):
        """Test that a valid status response is created correctly."""
        response = KeyStatusResponse(
            provider="google",
            key_hint="...1234",
            registered_at=datetime.now(timezone.utc),
            usage_count=5,
        )
        assert response.provider == "google"
        assert response.key_hint == "...1234"
        assert response.usage_count == 5

    def test_default_values(self):
        """Test that default values are set correctly."""
        response = KeyStatusResponse(provider="google", key_hint="...1234")
        assert response.registered_at is None
        assert response.expires_at is None
        assert response.last_used_at is None
        assert response.usage_count == 0


class TestValidateKeyRequest:
    """Test suite for ValidateKeyRequest model."""

    def test_valid_request(self):
        """Test that a valid validation request is created correctly."""
        request = ValidateKeyRequest(provider="google", api_key="test-key")
        assert request.provider == "google"
        assert request.api_key == "test-key"

    def test_default_provider(self):
        """Test that default provider is 'google'."""
        request = ValidateKeyRequest(api_key="test-key")
        assert request.provider == "google"


class TestValidateKeyResponse:
    """Test suite for ValidateKeyResponse model."""

    def test_valid_response(self):
        """Test that a valid validation response is created correctly."""
        response = ValidateKeyResponse(
            valid=True,
            models_available=["model1", "model2"],
        )
        assert response.valid is True
        assert response.error is None
        assert response.models_available == ["model1", "model2"]

    def test_invalid_response(self):
        """Test validation response for invalid key."""
        response = ValidateKeyResponse(
            valid=False,
            error="Invalid API key",
        )
        assert response.valid is False
        assert response.error == "Invalid API key"
        assert response.models_available == []

    def test_default_models(self):
        """Test that default models list is empty."""
        response = ValidateKeyResponse(valid=True)
        assert response.models_available == []


class TestKeyHintFormat:
    """Test suite for key hint format."""

    def test_key_hint_format(self):
        """Test that key hint follows expected format (...last4)."""
        api_key = "my-secret-api-key-1234"
        key_hint = f"...{api_key[-4:]}"
        assert key_hint == "...1234"
        assert key_hint.startswith("...")
        assert len(key_hint) == 7  # "..." + 4 chars

    def test_key_hint_short_key(self):
        """Test key hint with short key."""
        api_key = "abcd"
        key_hint = f"...{api_key[-4:]}"
        assert key_hint == "...abcd"

    def test_key_hint_single_char(self):
        """Test key hint with single character key."""
        api_key = "x"
        key_hint = f"...{api_key[-4:]}"
        assert key_hint == "...x"


class TestEncryptionIntegration:
    """Test suite for encryption service integration."""

    def test_encrypt_api_key(self):
        """Test that API key can be encrypted."""
        service = EncryptionService()
        api_key = "my-secret-api-key"

        encrypted = service.encrypt(api_key)

        assert encrypted is not None
        assert isinstance(encrypted, str)
        assert "encrypted_data" in encrypted
        assert "nonce" in encrypted
        assert "auth_tag" in encrypted

    def test_decrypt_api_key(self):
        """Test that encrypted API key can be decrypted."""
        service = EncryptionService()
        api_key = "my-secret-api-key"

        encrypted = service.encrypt(api_key)
        decrypted = service.decrypt(encrypted)

        assert decrypted == api_key


class TestValidationResult:
    """Test suite for ValidationResult dataclass."""

    def test_valid_result(self):
        """Test ValidationResult for valid key."""
        result = ValidationResult(
            valid=True,
            models_available=["models/gemini-3-flash-preview"],
        )
        assert result.valid is True
        assert result.error is None
        assert len(result.models_available) == 1

    def test_invalid_result(self):
        """Test ValidationResult for invalid key."""
        result = ValidationResult(
            valid=False,
            error="Invalid API key",
        )
        assert result.valid is False
        assert result.error == "Invalid API key"


class TestModelValidation:
    """Test suite for Pydantic model validation."""

    def test_register_request_missing_api_key(self):
        """Test that RegisterKeyRequest requires api_key."""
        with pytest.raises(ValidationError):
            RegisterKeyRequest(provider="google")

    def test_register_request_empty_api_key(self):
        """Test that empty api_key is accepted (not validated)."""
        request = RegisterKeyRequest(provider="google", api_key="")
        assert request.api_key == ""

    def test_validate_request_missing_api_key(self):
        """Test that ValidateKeyRequest requires api_key."""
        with pytest.raises(ValidationError):
            ValidateKeyRequest(provider="google")
