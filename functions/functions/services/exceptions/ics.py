from .base import SyncademicError


class BaseIcsError(SyncademicError):
    """Base class for ICS-related errors"""

    pass


class IcsSourceError(BaseIcsError):
    """Raised when there are issues with the ICS source"""

    pass


class IcsParsingError(BaseIcsError):
    """Raised when the ICS content cannot be parsed"""

    pass


class RecurringEventError(IcsParsingError):
    """Raised when a recurring event is detected because we don't support them yet."""

    pass
