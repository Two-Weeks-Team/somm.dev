# backend/tests/conftest.py
"""Pytest configuration and fixtures for somm.dev backend tests"""

import os
import sys
from pathlib import Path

os.environ.setdefault("GITHUB_CLIENT_ID", "test_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test_client_secret")

os.environ.pop("OPENAI_API_KEY", None)

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
