"""Encryption service for secure API key storage using AES-256-GCM.

This module provides encryption and decryption services for sensitive data
like API keys using AES-256-GCM authenticated encryption.
"""

import base64
import json
import logging
import os
import secrets
from typing import Optional

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Exception raised for encryption-related errors."""

    pass


class EncryptionService:
    """Service for encrypting and decrypting sensitive data using AES-256-GCM.

    This service uses AES-256-GCM authenticated encryption to ensure both
    confidentiality and integrity of encrypted data.

    Attributes:
        _key: The 32-byte encryption key used for AES-256 operations.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize the encryption service with a key.

        Args:
            encryption_key: Optional base64-encoded encryption key.
                If not provided, falls back to ENCRYPTION_KEY env var.
                In development mode without a key, a temporary key is generated.

        Raises:
            EncryptionError: If no key is provided in production mode.
        """
        self._key = self._resolve_key(encryption_key)

    def _resolve_key(self, provided_key: Optional[str]) -> bytes:
        """Resolve the encryption key from various sources.

        Priority order:
        1. Provided key parameter
        2. ENCRYPTION_KEY environment variable
        3. Auto-generated temporary key (development only)

        Args:
            provided_key: The key passed to the constructor.

        Returns:
            The 32-byte encryption key.

        Raises:
            EncryptionError: If no key is available in production.
        """
        key_str = provided_key or os.environ.get("ENCRYPTION_KEY")
        if key_str:
            return base64.b64decode(key_str)
        debug = os.environ.get("DEBUG", "true").lower() == "true"
        if debug:
            logger.warning(
                "No ENCRYPTION_KEY set. Generating temporary key for development."
            )
            return secrets.token_bytes(32)
        raise EncryptionError(
            "ENCRYPTION_KEY environment variable required in production"
        )

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: The string to encrypt.

        Returns:
            JSON string containing encrypted_data, nonce, and auth_tag.

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise EncryptionError(
                "cryptography package is required for encryption. "
                "Install it with: pip install cryptography"
            )

        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        # GCM appends auth_tag to ciphertext
        ct_bytes = ciphertext[:-16]
        auth_tag = ciphertext[-16:]
        return json.dumps(
            {
                "encrypted_data": base64.b64encode(ct_bytes).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "auth_tag": base64.b64encode(auth_tag).decode(),
            }
        )

    def decrypt(self, ciphertext_json: str) -> str:
        """Decrypt ciphertext using AES-256-GCM.

        Args:
            ciphertext_json: JSON string containing encrypted_data, nonce, and auth_tag.

        Returns:
            The decrypted plaintext string.

        Raises:
            EncryptionError: If decryption fails or authentication tag is invalid.
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise EncryptionError(
                "cryptography package is required for decryption. "
                "Install it with: pip install cryptography"
            )

        try:
            data = json.loads(ciphertext_json)
            ct_bytes = base64.b64decode(data["encrypted_data"])
            nonce = base64.b64decode(data["nonce"])
            auth_tag = base64.b64decode(data["auth_tag"])
            aesgcm = AESGCM(self._key)
            plaintext = aesgcm.decrypt(nonce, ct_bytes + auth_tag, None)
            return plaintext.decode()
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise EncryptionError(f"Invalid ciphertext format: {str(e)}")
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
