from .base import SyncademicError
from .auth import (
    BaseAuthorizationError,
    InvalidAuthCodeError,
    TokenVerificationError,
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
    "InvalidAuthCodeError",
    "TokenVerificationError",
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
