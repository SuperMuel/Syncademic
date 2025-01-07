from .base import SyncademicError


class BaseAuthorizationError(SyncademicError):
    """Base class for authorization-related errors"""

    pass


class InvalidAuthCodeError(BaseAuthorizationError):
    """Raised when the authorization code is invalid or expired"""

    pass


class TokenVerificationError(BaseAuthorizationError):
    """Raised when token verification fails"""

    pass
