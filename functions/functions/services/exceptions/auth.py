from .base import SyncademicError


class BaseAuthorizationError(SyncademicError):
    """Base class for authorization-related errors"""

    pass


class UnauthorizedError(BaseAuthorizationError):
    """Raised when Syncademic does not have permission to access the user's Google Calendar"""

    pass


class ProviderUserIdMismatchError(BaseAuthorizationError):
    """Raised when the authorization flow succeed, but for a different provider account
    than the one that was expected.

    Typically, the user would first select a provider account to link to their Syncademic, and
    then complete the authorization flow. The second flow might prompt the user to select a
    different account, which would raise this error.
    """

    pass
