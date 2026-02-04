# backend/tests/test_app.py
"""
Tests for the FastAPI application module structure.
RED Phase: These tests should FAIL initially because the app module doesn't exist yet.
"""


def test_import_app_main():
    """Test that the main FastAPI app can be imported from app.main"""
    from app.main import app

    assert app is not None


def test_import_app_main_app_object():
    """Test that the app object has correct type"""
    from app.main import app
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)


def test_import_app_core_config():
    """Test that the core config settings can be imported from app.core.config"""
    from app.core.config import settings

    assert settings is not None


def test_import_app_core_config_has_required_attributes():
    """Test that settings object has expected attributes"""
    from app.core.config import settings

    # Settings should have these attributes (will be defined in config.py)
    assert hasattr(settings, "APP_NAME")
    assert hasattr(settings, "API_V1_STR")
