from .base import SyncademicError


class BaseTargetCalendarError(SyncademicError):
    """Base class for calendar-related errors"""

    pass


class TargetCalendarNotFoundError(BaseTargetCalendarError):
    """Raised when a calendar cannot be found"""

    pass


class TargetCalendarAccessError(BaseTargetCalendarError):
    """Raised when there are permission issues with a calendar"""

    pass
