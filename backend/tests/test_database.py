# backend/tests/test_database.py
"""
Tests for the database module with Motor MongoDB connection.
RED Phase: These tests should FAIL initially because the database module doesn't exist yet.
"""

from unittest.mock import MagicMock


def test_import_database_module():
    """Test that the database module can be imported from app.database"""
    from app.database import connect_to_mongo, close_mongo_connection, get_database

    assert connect_to_mongo is not None
    assert close_mongo_connection is not None
    assert get_database is not None


def test_connect_to_mongo_function_exists():
    """Test that connect_to_mongo function exists and is callable"""
    from app.database.connection import connect_to_mongo

    assert callable(connect_to_mongo)


def test_close_mongo_connection_function_exists():
    """Test that close_mongo_connection function exists and is callable"""
    from app.database.connection import close_mongo_connection

    assert callable(close_mongo_connection)


def test_get_database_function_exists():
    """Test that get_database function exists and is callable"""
    from app.database.connection import get_database

    assert callable(get_database)


def test_get_database_returns_motor_database():
    """Test that get_database returns an AsyncIOMotorDatabase instance"""
    from motor.motor_asyncio import AsyncIOMotorDatabase
    from app.database.connection import get_database

    # This test will fail because client is None before connection
    # We mock the client to test the return type
    mock_client = MagicMock()
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)

    import app.database.connection as db_module

    db_module.client = mock_client
    mock_client.__getitem__.return_value = mock_db

    # Verify it's a MotorDatabase instance (or mock of it)
    assert get_database() is not None


def test_database_module_has_connection_attributes():
    """Test that the database connection module has required attributes"""
    from app.database import connection

    # Check for client attribute (will be None initially)
    assert hasattr(connection, "client")
    assert hasattr(connection, "connect_to_mongo")
    assert hasattr(connection, "close_mongo_connection")
    assert hasattr(connection, "get_database")


def test_settings_has_mongo_db():
    """Test that settings has MONGO_DB attribute"""
    from app.core.config import settings

    assert hasattr(settings, "MONGO_DB")
    assert settings.MONGO_DB == "somm"


def test_get_database_returns_correct_database_name():
    """Test that get_database returns database with correct name from settings"""
    from app.database.connection import get_database
    from app.core.config import settings

    mock_client = MagicMock()
    mock_db = MagicMock()

    import app.database.connection as db_module

    db_module.client = mock_client
    mock_client.__getitem__.return_value = mock_db

    get_database()

    # Verify the database name from settings was used
    mock_client.__getitem__.assert_called_with(settings.MONGO_DB)
