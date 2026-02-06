"""API dependencies for authentication and common operations."""

from typing import Optional

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.database.repositories.user import UserRepository
from app.core.config import settings

security = HTTPBearer(auto_error=False)


class User:
    """User class for dependency injection containing user information."""

    def __init__(
        self,
        id: str,
        github_id: str,
        username: str,
        email: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ):
        self.id = id
        self.github_id = github_id
        self.username = username
        self.email = email
        self.avatar_url = avatar_url


def decode_token(token: str) -> dict:
    """Decode and validate JWT token.

    Args:
        token: The JWT token to decode.

    Returns:
        Decoded token payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """Get the current authenticated user from JWT token.

    This dependency extracts the JWT token from the Authorization header,
    query parameter, or request body and validates it.

    Token sources (in priority order):
    1. Authorization header (Bearer token)
    2. Query parameter (?token=xxx) - useful for SSE/EventSource connections

    Args:
        request: The FastAPI request object.
        credentials: HTTP Bearer credentials from Authorization header.

    Returns:
        The current authenticated user.

    Raises:
        HTTPException: If authentication fails (401) or user not found (404).
    """
    # Try to get token from Authorization header
    token = None

    if credentials:
        token = credentials.credentials
    else:
        # Try to get from Authorization header directly
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    # Fallback: Try to get from query parameter (for SSE/EventSource)
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please provide a valid token.",
        )

    # Decode and validate token
    payload = decode_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: missing user ID.",
        )

    # Get user from database
    user_repo = UserRepository()
    user_doc = await user_repo.get_by_id(user_id)

    if not user_doc:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return User(
        id=str(user_doc["_id"]),
        github_id=str(user_doc.get("github_id", "")),
        username=user_doc.get("username", ""),
        email=user_doc.get("email"),
        avatar_url=user_doc.get("avatar_url"),
    )


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None.

    This is a non-strict version of get_current_user that returns None
    instead of raising an exception when authentication fails.

    Args:
        request: The FastAPI request object.
        credentials: HTTP Bearer credentials from Authorization header.

    Returns:
        The current user or None if not authenticated.
    """
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None


async def get_current_user_token(
    user: User = Depends(get_current_user),
) -> str:
    """Get the GitHub access token for the current authenticated user.

    This dependency retrieves the user's GitHub access token from the database.
    Useful for making authenticated requests to GitHub API on behalf of the user.

    Args:
        user: The current authenticated user (from get_current_user dependency).

    Returns:
        The user's GitHub access token.

    Raises:
        HTTPException: If token is not available (404).
    """
    user_repo = UserRepository()
    user_doc = await user_repo.get_by_id(user.id)

    if not user_doc:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    token = user_doc.get("github_access_token")
    if not token:
        raise HTTPException(
            status_code=404,
            detail="GitHub access token not found. Please re-authenticate.",
        )

    return token
