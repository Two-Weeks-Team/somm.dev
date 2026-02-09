"""Tests for the encryption service."""

import json
import os
from unittest import mock

import pytest

from app.services.encryption import EncryptionService, EncryptionError


class TestEncryptionService:
    """Test suite for EncryptionService."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt then decrypt returns the original plaintext."""
        service = EncryptionService()
        plaintext = "my-secret-api-key-12345"

        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_different_nonces(self):
        """Test that two encryptions of same plaintext produce different ciphertext."""
        service = EncryptionService()
        plaintext = "same-text"

        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(plaintext)

        data1 = json.loads(encrypted1)
        data2 = json.loads(encrypted2)

        assert data1["encrypted_data"] != data2["encrypted_data"]
        assert data1["nonce"] != data2["nonce"]

    def test_tampered_ciphertext_fails(self):
        """Test that modifying encrypted data raises an error."""
        service = EncryptionService()
        plaintext = "secret-data"

        encrypted = service.encrypt(plaintext)
        data = json.loads(encrypted)

        ct_bytes = data["encrypted_data"]
        modified_ct = ct_bytes[:-4] + "XXXX"
        data["encrypted_data"] = modified_ct

        tampered = json.dumps(data)

        with pytest.raises(EncryptionError):
            service.decrypt(tampered)

    def test_tampered_nonce_fails(self):
        """Test that modifying nonce raises an error."""
        service = EncryptionService()
        plaintext = "secret-data"

        encrypted = service.encrypt(plaintext)
        data = json.loads(encrypted)

        nonce = data["nonce"]
        modified_nonce = nonce[:-4] + "XXXX"
        data["nonce"] = modified_nonce

        tampered = json.dumps(data)

        with pytest.raises(EncryptionError):
            service.decrypt(tampered)

    def test_tampered_auth_tag_fails(self):
        """Test that modifying auth_tag raises an error."""
        service = EncryptionService()
        plaintext = "secret-data"

        encrypted = service.encrypt(plaintext)
        data = json.loads(encrypted)

        auth_tag = data["auth_tag"]
        modified_tag = auth_tag[:-4] + "XXXX"
        data["auth_tag"] = modified_tag

        tampered = json.dumps(data)

        with pytest.raises(EncryptionError):
            service.decrypt(tampered)

    def test_dev_mode_generates_key(self):
        """Test that without ENCRYPTION_KEY env, dev mode generates temp key."""
        with mock.patch.dict(os.environ, {"DEBUG": "true"}, clear=True):
            if "ENCRYPTION_KEY" in os.environ:
                del os.environ["ENCRYPTION_KEY"]

            service = EncryptionService()
            assert service._key is not None
            assert len(service._key) == 32

    def test_production_requires_key(self):
        """Test that production mode requires ENCRYPTION_KEY."""
        with (
            mock.patch.dict(os.environ, {"DEBUG": "false"}, clear=True),
            pytest.raises(EncryptionError) as exc_info,
        ):
            if "ENCRYPTION_KEY" in os.environ:
                del os.environ["ENCRYPTION_KEY"]

            EncryptionService()

        assert "ENCRYPTION_KEY environment variable required" in str(exc_info.value)

    def test_provided_key(self):
        """Test that a provided key is used correctly."""
        import base64

        key = base64.b64encode(b"x" * 32).decode()
        service = EncryptionService(encryption_key=key)

        plaintext = "test-data"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_invalid_ciphertext_format(self):
        """Test that invalid ciphertext format raises error."""
        service = EncryptionService()

        with pytest.raises(EncryptionError):
            service.decrypt("not-valid-json")

        with pytest.raises(EncryptionError):
            service.decrypt('{"invalid": "format"}')

    def test_unicode_support(self):
        """Test encryption/decryption of unicode characters."""
        service = EncryptionService()
        plaintext = "日本語テキスト🎉🔐"

        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_empty_string(self):
        """Test encryption/decryption of empty string."""
        service = EncryptionService()
        plaintext = ""

        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_long_text(self):
        """Test encryption/decryption of long text."""
        service = EncryptionService()
        plaintext = "A" * 10000

        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext
