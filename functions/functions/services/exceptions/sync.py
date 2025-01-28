from .base import SyncademicError


class BaseSynchronizationError(SyncademicError):
    """Base class for synchronization-related errors"""

    pass


class SyncProfileNotFoundError(BaseSynchronizationError):
    """Raised when a sync profile cannot be found"""

    pass


class DailySyncLimitExceededError(BaseSynchronizationError):
    """Raised when daily synchronization limit is exceeded"""

    pass


class SyncInProgressError(BaseSynchronizationError):
    """Raised when a sync is already in progress"""

    pass
