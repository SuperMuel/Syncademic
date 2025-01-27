from .base import SyncademicError
from .auth import (
    BaseAuthorizationError,
    UnauthorizedError,
    ProviderUserIdMismatchError,
)
from .target_calendar import (
    BaseTargetCalendarError,
    TargetCalendarNotFoundError,
    TargetCalendarAccessError,
)
from .sync import (
    BaseSynchronizationError,
    SyncProfileNotFoundError,
    DailySyncLimitExceededError,
    SyncInProgressError,
)
from .ics import (
    IcsError,
    IcsUrlError,
    IcsParsingError,
)
from .ruleset import (
    BaseRulesetError,
    RulesetGenerationError,
    RulesetValidationError,
)
from .mapping import ErrorMapping

__all__ = [
    "SyncademicError",
    "BaseAuthorizationError",
    "ProviderUserIdMismatchError",
    "BaseTargetCalendarError",
    "TargetCalendarNotFoundError",
    "TargetCalendarAccessError",
    "BaseSynchronizationError",
    "SyncProfileNotFoundError",
    "DailySyncLimitExceededError",
    "SyncInProgressError",
    "IcsError",
    "IcsUrlError",
    "IcsParsingError",
    "BaseRulesetError",
    "RulesetGenerationError",
    "RulesetValidationError",
    "ErrorMapping",
]
