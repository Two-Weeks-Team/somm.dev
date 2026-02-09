"""Wine-themed custom exceptions for somm.dev backend.

This module provides custom HTTP exceptions with wine-themed naming:
- CorkedError: Bad Request (400)
- NoInvitationError: Unauthorized (401)
- EmptyCellarError: Not Found (404)
- OverconsumptionError: Rate Limit (429)
- SpoiledBatchError: Internal Server Error (500)
"""

from fastapi import HTTPException, status


class CorkedError(HTTPException):
    """Exception for bad request errors.

    Raised when the client sends invalid data or makes an invalid request.
    Corresponds to HTTP 400 Bad Request by default, but can be overridden.

    The term "corked" refers to wine that has been spoiled by a faulty cork,
    analogous to a spoiled or invalid request.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request data - the request is corked"

    def __init__(self, detail: str = None, status_code: int = None):
        super().__init__(
            status_code=status_code or self.__class__.status_code,
            detail=detail or self.default_detail,
        )


class NoInvitationError(HTTPException):
    """Exception for unauthorized access errors.

    Raised when authentication is required but not provided.
    Corresponds to HTTP 401 Unauthorized.

    The term "no invitation" refers to not having access privileges,
    similar to not having an invitation to a wine tasting event.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication required - no invitation provided"

    def __init__(self, detail: str = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
        )


class EmptyCellarError(HTTPException):
    """Exception for resource not found errors.

    Raised when a requested resource does not exist.
    Corresponds to HTTP 404 Not Found.

    The term "empty cellar" refers to a wine cellar with no wines,
    analogous to a requested resource that doesn't exist.
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found - the cellar is empty"

    def __init__(self, detail: str = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
        )


class OverconsumptionError(HTTPException):
    """Exception for rate limiting errors.

    Raised when the client has sent too many requests.
    Corresponds to HTTP 429 Too Many Requests.

    The term "overconsumption" refers to drinking too much wine,
    analogous to making too many requests.
    """

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded - please slow down your consumption"

    def __init__(self, detail: str = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
        )


class SpoiledBatchError(HTTPException):
    """Exception for internal server errors.

    Raised when an unexpected error occurs on the server.
    Corresponds to HTTP 500 Internal Server Error.

    The term "spoiled batch" refers to wine that has gone bad during fermentation,
    analogous to a server error that spoiled the processing.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error - the batch was spoiled"

    def __init__(self, detail: str = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
        )
