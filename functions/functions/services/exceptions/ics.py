from .base import SyncademicError


class IcsError(SyncademicError):
    """Base class for ICS-related errors"""

    pass


class IcsUrlError(IcsError):
    """Raised when there are issues with the ICS URL"""

    pass


class IcsParsingError(IcsError):
    """Raised when the ICS content cannot be parsed"""

    pass
