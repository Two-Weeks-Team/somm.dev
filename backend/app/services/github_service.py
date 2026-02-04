"""GitHub service for repository operations.

This module provides functionality to interact with the GitHub API:
- Parse GitHub URLs to extract owner/repo
- Fetch repository metadata
- Get file tree structure
- Fetch README content
- Analyze programming language breakdown
"""

import re
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.exceptions import CorkedError, EmptyCellarError

GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repository name from a GitHub URL.

    Args:
        url: A GitHub repository URL.

    Returns:
        A tuple of (owner, repo_name).

    Raises:
        CorkedError: If the URL is not a valid GitHub URL or is missing components.
    """
    if not url:
        raise CorkedError("URL cannot be empty")

    if not re.match(r"^https?://(www\.)?github\.com/", url):
        raise CorkedError("URL must be a GitHub repository URL")

    pattern = r"github\.com[/:]([^/]+)/([^/.]+)"
    match = re.search(pattern, url)

    if not match:
        raise CorkedError("Invalid GitHub URL format")

    owner, repo = match.groups()

    repo = repo.replace(".git", "")

    return owner, repo


class GitHubService:
    """Service for interacting with the GitHub API."""

    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub service.

        Args:
            token: Optional GitHub API token for authenticated requests.
        """
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def _get(self, url: str) -> httpx.Response:
        """Make a GET request to the GitHub API.

        Args:
            url: The API endpoint URL.

        Returns:
            The HTTP response.

        Raises:
            EmptyCellarError: If the resource is not found (404).
            CorkedError: For other API errors (403, 429, etc.).
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)

            if response.status_code == 404:
                raise EmptyCellarError(f"Resource not found: {url}")
            elif response.status_code == 403:
                raise CorkedError("GitHub API rate limit exceeded or access denied")
            elif response.status_code == 401:
                raise CorkedError("GitHub API authentication failed")
            elif not response.is_success:
                raise CorkedError(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )

            return response

    async def get_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository metadata from GitHub API.

        Args:
            owner: Repository owner username.
            repo: Repository name.

        Returns:
            A dictionary containing repository metadata.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        response = await self._get(url)
        return response.json()

    async def get_file_tree(
        self, owner: str, repo: str, branch: str = "main", recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """Get the file tree structure of a repository.

        Args:
            owner: Repository owner username.
            repo: Repository name.
            branch: Branch name to fetch from.
            recursive: Whether to recursively fetch all files.

        Returns:
            A list of file/tree item dictionaries.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}"
        if recursive:
            url = f"{url}?recursive=1"

        response = await self._get(url)
        data = response.json()
        return data.get("tree", [])

    async def get_readme(
        self, owner: str, repo: str, branch: str = "main"
    ) -> Optional[str]:
        """Fetch the README content of a repository.

        Args:
            owner: Repository owner username.
            repo: Repository name.
            branch: Branch name to fetch from.

        Returns:
            The README content as a string, or None if not found.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code == 404:
                return None

            if not response.is_success:
                raise CorkedError(f"Failed to fetch README: {response.status_code}")

            data = response.json()
            content = data.get("content", "")
            encoding = data.get("encoding", "base64")

            if encoding == "base64":
                import base64

                return base64.b64decode(content).decode("utf-8")

            return content

    async def analyze_languages(
        self, owner: str, repo: str
    ) -> Dict[str, Dict[str, float]]:
        """Analyze the programming language breakdown of a repository.

        Args:
            owner: Repository owner username.
            repo: Repository name.

        Returns:
            A dictionary mapping language names to their statistics,
            including byte count and percentage.
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
        response = await self._get(url)
        languages_data = response.json()

        total_bytes = sum(languages_data.values())
        languages = {}

        for language, bytes_count in languages_data.items():
            percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            languages[language] = {
                "bytes": bytes_count,
                "percentage": round(percentage, 2),
            }

        return languages

    async def get_full_repo_context(
        self, owner: str, repo: str, branch: str = "main"
    ) -> Dict[str, Any]:
        """Get a comprehensive context of a repository.

        This method fetches metadata, language breakdown, and file tree.

        Args:
            owner: Repository owner username.
            repo: Repository name.
            branch: Branch name to fetch from.

        Returns:
            A dictionary containing all repository context information.
        """
        metadata = await self.get_repo_metadata(owner, repo)
        languages = await self.analyze_languages(owner, repo)
        file_tree = await self.get_file_tree(owner, repo, branch, recursive=True)
        readme = await self.get_readme(owner, repo, branch)

        return {
            "metadata": {
                "name": metadata.get("name"),
                "full_name": metadata.get("full_name"),
                "description": metadata.get("description"),
                "stars": metadata.get("stargazers_count"),
                "forks": metadata.get("forks_count"),
                "language": metadata.get("language"),
                "default_branch": metadata.get("default_branch"),
                "owner": metadata.get("owner", {}).get("login"),
            },
            "languages": languages,
            "file_tree": file_tree,
            "readme": readme,
        }
