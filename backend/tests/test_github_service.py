"""Tests for GitHub service module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.exceptions import CorkedError, EmptyCellarError


class TestParseGitHubURL:
    """Test cases for parse_github_url function."""

    def test_parse_github_url_with_https(self):
        """Test parsing a standard GitHub HTTPS URL."""
        from app.services.github_service import parse_github_url

        result = parse_github_url("https://github.com/owner/repo")
        assert result == ("owner", "repo")

    def test_parse_github_url_with_git_extension(self):
        """Test parsing a GitHub URL with .git extension."""
        from app.services.github_service import parse_github_url

        result = parse_github_url("https://github.com/owner/repo.git")
        assert result == ("owner", "repo")

    def test_parse_github_url_with_www(self):
        """Test parsing a GitHub URL with www prefix."""
        from app.services.github_service import parse_github_url

        result = parse_github_url("https://www.github.com/owner/repo")
        assert result == ("owner", "repo")

    def test_parse_github_url_with_branch(self):
        """Test parsing a GitHub URL with branch path."""
        from app.services.github_service import parse_github_url

        result = parse_github_url("https://github.com/owner/repo/tree/main")
        assert result == ("owner", "repo")

    def test_parse_github_url_with_dashes_in_name(self):
        """Test parsing a GitHub URL with dashes in owner/repo names."""
        from app.services.github_service import parse_github_url

        result = parse_github_url("https://github.com/my-org/my-awesome-repo")
        assert result == ("my-org", "my-awesome-repo")

    def test_parse_github_url_invalid_url(self):
        """Test parsing an invalid URL raises CorkedError."""
        from app.services.github_service import parse_github_url

        with pytest.raises(CorkedError):
            parse_github_url("https://gitlab.com/owner/repo")

    def test_parse_github_url_missing_parts(self):
        """Test parsing URL with missing owner/repo raises CorkedError."""
        from app.services.github_service import parse_github_url

        with pytest.raises(CorkedError):
            parse_github_url("https://github.com/owner")

    def test_parse_github_url_empty_url(self):
        """Test parsing empty URL raises CorkedError."""
        from app.services.github_service import parse_github_url

        with pytest.raises(CorkedError):
            parse_github_url("")


class TestGitHubServiceInstantiation:
    """Test cases for GitHubService instantiation."""

    def test_github_service_without_token(self):
        """Test GitHub service initialization without token."""
        from app.services.github_service import GitHubService

        service = GitHubService()
        assert service.token is None

    def test_github_service_with_token(self):
        """Test GitHub service initialization with token."""
        from app.services.github_service import GitHubService

        service = GitHubService(token="test_token")
        assert service.token == "test_token"
        assert "Authorization" in service.headers


class TestGitHubServiceMocked:
    """Test cases for GitHubService with mocked responses."""

    @pytest.mark.asyncio
    async def test_get_repo_metadata_success(self):
        """Test fetching repository metadata successfully."""
        from app.services.github_service import GitHubService

        mock_response_data = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "A test repository",
            "stargazers_count": 100,
            "forks_count": 50,
            "language": "Python",
            "default_branch": "main",
            "owner": {"login": "owner"},
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()
            result = await service.get_repo_metadata("owner", "test-repo")

            assert result["name"] == "test-repo"
            assert result["full_name"] == "owner/test-repo"
            assert result["stargazers_count"] == 100

    @pytest.mark.asyncio
    async def test_get_repo_metadata_not_found(self):
        """Test fetching metadata for non-existent repository raises EmptyCellarError."""
        from app.services.github_service import GitHubService

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()

            with pytest.raises(EmptyCellarError):
                await service.get_repo_metadata("nonexistent", "repo")

    @pytest.mark.asyncio
    async def test_get_repo_metadata_rate_limited(self):
        """Test handling rate limiting from GitHub API."""
        from app.services.github_service import GitHubService

        mock_response = MagicMock()
        mock_response.status_code = 403

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()

            with pytest.raises(CorkedError):
                await service.get_repo_metadata("owner", "repo")

    @pytest.mark.asyncio
    async def test_get_file_tree_success(self):
        """Test fetching repository file tree successfully."""
        from app.services.github_service import GitHubService

        mock_tree = [
            {"path": "src/main.py", "type": "blob", "size": 1024},
            {"path": "tests/test_main.py", "type": "blob", "size": 512},
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"tree": mock_tree})

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()
            result = await service.get_file_tree("owner", "repo", "main")

            assert len(result) == 2
            assert result[0]["path"] == "src/main.py"

    @pytest.mark.asyncio
    async def test_get_readme_not_found(self):
        """Test fetching README when repository has no README."""
        from app.services.github_service import GitHubService

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()

            result = await service.get_readme("owner", "repo", "main")
            assert result is None

    @pytest.mark.asyncio
    async def test_analyze_languages_success(self):
        """Test analyzing repository language breakdown."""
        from app.services.github_service import GitHubService

        mock_languages = {
            "Python": 5000,
            "JavaScript": 2000,
            "TypeScript": 1000,
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value=mock_languages)

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()
            result = await service.analyze_languages("owner", "repo")

            assert "Python" in result
            assert "JavaScript" in result
            assert "TypeScript" in result

    @pytest.mark.asyncio
    async def test_analyze_languages_empty_repo(self):
        """Test analyzing empty repository languages."""
        from app.services.github_service import GitHubService

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={})

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = GitHubService()
            result = await service.analyze_languages("owner", "repo")

            assert len(result) == 0
