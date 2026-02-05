"""Repository API routes for fetching user GitHub repositories.

This module provides endpoints for:
- Listing user's GitHub repositories (from cache or fresh from GitHub)
- Refreshing the repository cache
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_token, User
from app.database.repositories.repository_cache import RepositoryCacheRepository
from app.models.repository import RepositoryBase, RepositoryListResponse
from app.services.github_service import GitHubService

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("", response_model=RepositoryListResponse)
async def get_repositories(
    user: User = Depends(get_current_user),
    token: str = Depends(get_current_user_token),
) -> RepositoryListResponse:
    """Get user's GitHub repositories.

    This endpoint returns the user's repositories from cache if available,
    or fetches fresh data from GitHub API if cache is missing or expired.

    Args:
        user: The current authenticated user.
        token: The user's GitHub access token.

    Returns:
        RepositoryListResponse containing list of repositories and metadata.

    Raises:
        HTTPException: If authentication fails or GitHub API error occurs.
    """
    cache_repo = RepositoryCacheRepository()

    # Check if we have valid cached data
    cached_repos = await cache_repo.get_user_repos(user.id)

    if cached_repos:
        # Transform cached documents to RepositoryBase models
        repositories = []
        for repo_doc in cached_repos:
            # Remove MongoDB-specific fields
            repo_data = {
                k: v for k, v in repo_doc.items()
                if k not in ("_id", "user_id", "cached_at")
            }
            repositories.append(RepositoryBase(**repo_data))

        cached_at = cached_repos[0].get("cached_at")

        return RepositoryListResponse(
            repositories=repositories,
            total=len(repositories),
            cached_at=cached_at,
        )

    # No cache - fetch from GitHub
    try:
        github_service = GitHubService()
        repos_data = await github_service.list_user_repositories(token)

        # Cache the results
        await cache_repo.set_user_repos(user.id, repos_data)

        # Transform to RepositoryBase models
        repositories = [RepositoryBase(**repo) for repo in repos_data]

        return RepositoryListResponse(
            repositories=repositories,
            total=len(repositories),
            cached_at=None,  # Fresh data, not from cache
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch repositories from GitHub: {str(e)}",
        )


@router.post("/refresh", response_model=RepositoryListResponse)
async def refresh_repositories(
    user: User = Depends(get_current_user),
    token: str = Depends(get_current_user_token),
) -> RepositoryListResponse:
    """Refresh user's GitHub repositories cache.

    This endpoint clears the cache and fetches fresh data from GitHub API.

    Args:
        user: The current authenticated user.
        token: The user's GitHub access token.

    Returns:
        RepositoryListResponse containing fresh list of repositories.

    Raises:
        HTTPException: If authentication fails or GitHub API error occurs.
    """
    cache_repo = RepositoryCacheRepository()

    # Clear existing cache
    await cache_repo.clear_user_repos(user.id)

    # Fetch fresh data from GitHub
    try:
        github_service = GitHubService()
        repos_data = await github_service.list_user_repositories(token)

        # Cache the new results
        await cache_repo.set_user_repos(user.id, repos_data)

        # Transform to RepositoryBase models
        repositories = [RepositoryBase(**repo) for repo in repos_data]

        return RepositoryListResponse(
            repositories=repositories,
            total=len(repositories),
            cached_at=None,  # Fresh data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh repositories from GitHub: {str(e)}",
        )
