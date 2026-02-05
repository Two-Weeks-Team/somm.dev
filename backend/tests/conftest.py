# backend/tests/conftest.py
"""Pytest configuration and fixtures for somm.dev backend tests"""

import os
import sys
from pathlib import Path

# Set required environment variables BEFORE any app imports
# This ensures Settings validation passes when the module is first loaded
os.environ.setdefault("GITHUB_CLIENT_ID", "test_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test_client_secret")

# Add the backend directory to the Python path so we can import 'app'
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
