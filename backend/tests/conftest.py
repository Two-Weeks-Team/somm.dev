# backend/tests/conftest.py
"""Pytest fixtures for somm.dev backend tests with auth bypass support."""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from jose import jwt

os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_testing_purposes_only"
os.environ.setdefault("GITHUB_CLIENT_ID", "test_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test_client_secret")
os.environ.pop("OPENAI_API_KEY", None)

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture(autouse=True)
def mock_mongo_connection():
    """Auto-mock MongoDB connection for all tests."""
    with (
        patch(
            "app.database.connection.connect_to_mongo", new_callable=AsyncMock
        ) as mock_connect,
        patch(
            "app.database.connection.close_mongo_connection", new_callable=AsyncMock
        ) as mock_close,
        patch("app.database.connect_to_mongo", new_callable=AsyncMock),
        patch("app.database.close_mongo_connection", new_callable=AsyncMock),
        patch("app.main.connect_to_mongo", new_callable=AsyncMock),
        patch("app.main.close_mongo_connection", new_callable=AsyncMock),
    ):
        yield mock_connect, mock_close


@pytest.fixture
def test_user_data() -> dict:
    """Raw user data as stored in database."""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "github_id": "12345678",
        "username": "testuser",
        "email": "test@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
        "role": "user",
        "plan": "free",
        "github_access_token": "gho_test_token_12345",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def admin_user_data() -> dict:
    """Admin user data for testing admin endpoints."""
    return {
        "_id": "507f1f77bcf86cd799439012",
        "github_id": "87654321",
        "username": "adminuser",
        "email": "admin@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/87654321",
        "role": "admin",
        "plan": "pro",
        "github_access_token": "gho_admin_token_12345",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def mock_user(test_user_data: dict):
    """Mock User object for dependency injection."""
    from app.api.deps import User

    return User(
        id=str(test_user_data["_id"]),
        github_id=test_user_data["github_id"],
        username=test_user_data["username"],
        email=test_user_data["email"],
        avatar_url=test_user_data["avatar_url"],
        role=test_user_data["role"],
        plan=test_user_data["plan"],
    )


@pytest.fixture
def mock_admin_user(admin_user_data: dict):
    """Mock admin User object for dependency injection."""
    from app.api.deps import User

    return User(
        id=str(admin_user_data["_id"]),
        github_id=admin_user_data["github_id"],
        username=admin_user_data["username"],
        email=admin_user_data["email"],
        avatar_url=admin_user_data["avatar_url"],
        role=admin_user_data["role"],
        plan=admin_user_data["plan"],
    )


@pytest.fixture
def test_jwt_token(test_user_data: dict) -> str:
    """Generate valid JWT token for testing."""
    from app.core.config import settings

    payload = {
        "sub": str(test_user_data["_id"]),
        "github_id": test_user_data["github_id"],
        "username": test_user_data["username"],
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


@pytest.fixture
def admin_jwt_token(admin_user_data: dict) -> str:
    """Generate valid JWT token for admin user."""
    from app.core.config import settings

    payload = {
        "sub": str(admin_user_data["_id"]),
        "github_id": admin_user_data["github_id"],
        "username": admin_user_data["username"],
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


@pytest.fixture
def auth_headers(test_jwt_token: str) -> dict:
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {test_jwt_token}"}


@pytest.fixture
def admin_auth_headers(admin_jwt_token: str) -> dict:
    """Authorization headers with admin Bearer token."""
    return {"Authorization": f"Bearer {admin_jwt_token}"}


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Synchronous test client without auth bypass."""
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_client(mock_user, test_user_data: dict) -> Generator[TestClient, None, None]:
    """Test client with auth bypassed via dependency override."""
    from app.main import app
    from app.api.deps import get_current_user, get_current_user_token, get_optional_user

    async def override_get_current_user():
        return mock_user

    async def override_get_optional_user():
        return mock_user

    async def override_get_current_user_token():
        return test_user_data["github_access_token"]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_optional_user] = override_get_optional_user
    app.dependency_overrides[get_current_user_token] = override_get_current_user_token

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(
    mock_admin_user, admin_user_data: dict
) -> Generator[TestClient, None, None]:
    """Test client with admin auth bypassed."""
    from app.main import app
    from app.api.deps import get_current_user, get_current_user_token, get_optional_user
    from app.api.routes.admin import require_admin

    async def override_get_current_user():
        return mock_admin_user

    async def override_get_optional_user():
        return mock_admin_user

    async def override_get_current_user_token():
        return admin_user_data["github_access_token"]

    async def override_require_admin():
        return mock_admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_optional_user] = override_get_optional_user
    app.dependency_overrides[get_current_user_token] = override_get_current_user_token
    app.dependency_overrides[require_admin] = override_require_admin

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client without auth bypass."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def async_auth_client(
    mock_user, test_user_data: dict
) -> AsyncGenerator[AsyncClient, None]:
    """Async test client with auth bypassed."""
    from app.main import app
    from app.api.deps import get_current_user, get_current_user_token, get_optional_user

    async def override_get_current_user():
        return mock_user

    async def override_get_optional_user():
        return mock_user

    async def override_get_current_user_token():
        return test_user_data["github_access_token"]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_optional_user] = override_get_optional_user
    app.dependency_overrides[get_current_user_token] = override_get_current_user_token

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_evaluation_data(test_user_data: dict) -> dict:
    """Mock evaluation document."""
    return {
        "_id": "eval_507f1f77bcf86cd799439099",
        "evaluation_id": "eval_507f1f77bcf86cd799439099",
        "user_id": str(test_user_data["_id"]),
        "repo_context": {
            "repo_url": "https://github.com/testuser/testrepo",
            "owner": "testuser",
            "repo": "testrepo",
            "branch": "main",
        },
        "criteria": "basic",
        "status": "completed",
        "evaluation_mode": "six_sommeliers",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "methodology_trace": [],
    }


@pytest.fixture
def mock_result_data(mock_evaluation_data: dict) -> dict:
    """Mock evaluation result document."""
    return {
        "evaluation_id": mock_evaluation_data["evaluation_id"],
        "final_evaluation": {
            "score": 85,
            "rating_tier": "Premier Cru",
            "summary": "A well-crafted repository with solid fundamentals.",
            "sommelier_outputs": {
                "marcel": {"score": 82, "analysis": "Good structure"},
                "isabella": {"score": 88, "analysis": "Excellent code quality"},
                "heinrich": {"score": 80, "analysis": "Adequate testing"},
                "sofia": {"score": 90, "analysis": "Innovative approach"},
                "laurent": {"score": 85, "analysis": "Solid implementation"},
            },
            "jean_pierre_verdict": "This repository demonstrates professional development practices.",
        },
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def mock_repository_data() -> list:
    """Mock GitHub repository list."""
    return [
        {
            "id": 123456789,
            "name": "testrepo",
            "full_name": "testuser/testrepo",
            "html_url": "https://github.com/testuser/testrepo",
            "description": "A test repository",
            "language": "Python",
            "stargazers_count": 42,
            "forks_count": 10,
            "private": False,
            "updated_at": datetime.utcnow().isoformat(),
        },
        {
            "id": 987654321,
            "name": "another-repo",
            "full_name": "testuser/another-repo",
            "html_url": "https://github.com/testuser/another-repo",
            "description": "Another test repository",
            "language": "TypeScript",
            "stargazers_count": 100,
            "forks_count": 25,
            "private": False,
            "updated_at": datetime.utcnow().isoformat(),
        },
    ]


@pytest.fixture
def mock_user_repository(test_user_data: dict):
    """Mock UserRepository for testing without database."""
    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=test_user_data)
    mock_repo.get_by_github_id = AsyncMock(return_value=test_user_data)
    mock_repo.create = AsyncMock(return_value=str(test_user_data["_id"]))
    mock_repo.update = AsyncMock(return_value=True)
    mock_repo.list = AsyncMock(return_value=[test_user_data])
    return mock_repo


@pytest.fixture
def mock_evaluation_repository(mock_evaluation_data: dict, mock_result_data: dict):
    """Mock EvaluationRepository for testing without database."""
    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_evaluation_data)
    mock_repo.create = AsyncMock(return_value=mock_evaluation_data["evaluation_id"])
    mock_repo.update_status = AsyncMock(return_value=True)
    mock_repo.get_user_history = AsyncMock(return_value=[mock_evaluation_data])
    return mock_repo


@pytest.fixture
def mock_result_repository(mock_result_data: dict):
    """Mock ResultRepository for testing without database."""
    mock_repo = MagicMock()
    mock_repo.get_by_evaluation_id = AsyncMock(return_value=mock_result_data)
    mock_repo.save = AsyncMock(return_value=True)
    return mock_repo


@pytest.fixture
def mock_api_key_repository():
    """Mock APIKeyRepository for testing without database."""
    mock_repo = MagicMock()
    mock_repo.get_status = AsyncMock(return_value=[])
    mock_repo.get_key = AsyncMock(return_value=None)
    mock_repo.save_key = AsyncMock(
        return_value={"expires_at": datetime.utcnow() + timedelta(days=30)}
    )
    mock_repo.delete_key = AsyncMock(return_value=True)
    return mock_repo


@pytest.fixture
def mock_repository_cache():
    """Mock RepositoryCacheRepository for testing."""
    mock_repo = MagicMock()
    mock_repo.get_user_repos = AsyncMock(return_value=None)
    mock_repo.set_user_repos = AsyncMock(return_value=True)
    mock_repo.clear_user_repos = AsyncMock(return_value=True)
    return mock_repo


@pytest.fixture
def mock_github_service(mock_repository_data: list):
    """Mock GitHubService for testing without actual API calls."""
    mock_service = MagicMock()
    mock_service.list_user_repositories = AsyncMock(return_value=mock_repository_data)
    mock_service.get_repository = AsyncMock(return_value=mock_repository_data[0])
    return mock_service


@pytest.fixture
def mock_quota_result():
    """Mock quota check result."""
    from app.services.quota import QuotaResult

    return QuotaResult(
        allowed=True,
        reason="Quota available",
        remaining=5,
        daily_limit=10,
        used_today=5,
    )


@pytest.fixture(scope="session")
def event_loop_policy():
    """Event loop policy for async tests."""
    import asyncio

    return asyncio.DefaultEventLoopPolicy()
