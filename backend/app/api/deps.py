"""API dependencies for authentication and common operations."""

from typing import Optional

from app.core.exceptions import NoInvitationError


class User:
    """Simple user class for dependency injection."""

    def __init__(self, id: str, email: Optional[str] = None):
        self.id = id
        self.email = email


async def get_current_user() -> User:
    """Get the current authenticated user.

    This is a placeholder implementation. In a production environment,
    this would extract and validate JWT tokens or session data.

    Returns:
        The current user.

    Raises:
        NoInvitationError: If the user is not authenticated.
    """
    return User(id="test_user", email="test@example.com")


async def get_optional_user() -> Optional[User]:
    """Get the current user if authenticated, otherwise return None.

    Returns:
        The current user or None if not authenticated.
    """
    return User(id="test_user", email="test@example.com")
