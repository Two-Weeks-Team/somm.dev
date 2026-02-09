"""Tests for GitHubService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.github_service import GitHubService, parse_github_url
from app.core.exceptions import CorkedError


class TestParseGitHubUrl:
    """Test suite for parse_github_url function."""

    def test_valid_github_url(self):
        """Test parsing a valid GitHub URL."""
        owner, repo = parse_github_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_url_with_git_suffix(self):
        """Test parsing URL with .git suffix."""
        owner, repo = parse_github_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_empty_url_raises_error(self):
        """Test that empty URL raises CorkedError."""
        with pytest.raises(CorkedError, match="URL cannot be empty"):
            parse_github_url("")

    def test_non_github_url_raises_error(self):
        """Test that non-GitHub URL raises CorkedError."""
        with pytest.raises(CorkedError, match="URL must be a GitHub repository URL"):
            parse_github_url("https://gitlab.com/owner/repo")


class TestGitHubServiceListUserRepositories:
    """Test suite for list_user_repositories method."""

    @pytest.fixture
    def github_service(self):
        """Fixture for GitHubService instance."""
        return GitHubService()

    @pytest.fixture
    def sample_repo_response(self):
        """Fixture for sample repository response."""
        return [
            {
                "id": 1,
                "name": "repo1",
                "full_name": "owner/repo1",
                "description": "Test repo 1",
                "private": False,
                "html_url": "https://github.com/owner/repo1",
                "default_branch": "main",
                "stargazers_count": 10,
                "forks_count": 5,
                "language": "Python",
                "updated_at": "2024-01-01T00:00:00Z",
                "pushed_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": 2,
                "name": "repo2",
                "full_name": "owner/repo2",
                "description": None,
                "private": True,
                "html_url": "https://github.com/owner/repo2",
                "default_branch": "main",
                "stargazers_count": 0,
                "forks_count": 0,
                "language": None,
                "updated_at": "2024-01-02T00:00:00Z",
                "pushed_at": "2024-01-02T00:00:00Z",
            },
        ]

    @pytest.mark.asyncio
    async def test_list_user_repositories_returns_repos(
        self, github_service, sample_repo_response
    ):
        """Test that list_user_repositories returns list of repos."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_repo_response
        mock_response.headers = {"link": ""}  # No next page

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            repos = await github_service.list_user_repositories("test_token")

            assert len(repos) == 2
            assert repos[0]["name"] == "repo1"
            assert repos[0]["full_name"] == "owner/repo1"
            assert repos[0]["private"] is False
            assert repos[1]["name"] == "repo2"
            assert repos[1]["private"] is True

    @pytest.mark.asyncio
    async def test_list_user_repositories_handles_empty_list(self, github_service):
        """Test handling of empty repository list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.headers = {}

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            repos = await github_service.list_user_repositories("test_token")

            assert repos == []

    @pytest.mark.asyncio
    async def test_list_user_repositories_handles_pagination(self, github_service):
        """Test pagination handling via Link header."""
        page1_repos = [
            {
                "id": 1,
                "name": "repo1",
                "full_name": "owner/repo1",
                "private": False,
                "html_url": "https://github.com/owner/repo1",
                "default_branch": "main",
                "stargazers_count": 0,
                "forks_count": 0,
                "language": None,
                "updated_at": None,
                "pushed_at": None,
            }
        ]
        page2_repos = [
            {
                "id": 2,
                "name": "repo2",
                "full_name": "owner/repo2",
                "private": False,
                "html_url": "https://github.com/owner/repo2",
                "default_branch": "main",
                "stargazers_count": 0,
                "forks_count": 0,
                "language": None,
                "updated_at": None,
                "pushed_at": None,
            }
        ]

        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = page1_repos
        mock_response1.headers = {
            "link": '<https://api.github.com/user/repos?page=2>; rel="next"'
        }

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = page2_repos
        mock_response2.headers = {"link": ""}  # No next page

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [mock_response1, mock_response2]

            repos = await github_service.list_user_repositories("test_token")

            assert len(repos) == 2
            assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_list_user_repositories_handles_401_error(self, github_service):
        """Test that 401 error raises CorkedError."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(CorkedError, match="GitHub authentication failed"):
                await github_service.list_user_repositories("invalid_token")

    @pytest.mark.asyncio
    async def test_list_user_repositories_handles_403_rate_limit(self, github_service):
        """Test that 403 error raises CorkedError."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Rate limit exceeded"

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(CorkedError, match="rate limit exceeded"):
                await github_service.list_user_repositories("test_token")
