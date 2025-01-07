from firebase_functions import https_fn
from .base import SyncademicError
from .auth import BaseAuthorizationError
from .target_calendar import (
    TargetCalendarAccessError,
    TargetCalendarNotFoundError,
)
from .sync import (
    SyncInProgressError,
    SyncProfileNotFoundError,
    DailySyncLimitExceededError,
)
from .auth import InvalidAuthCodeError, TokenVerificationError
from .ruleset import RulesetGenerationError, RulesetValidationError

from .ics import IcsUrlError


class ErrorMapping:
    """Maps domain exceptions to Firebase Functions error codes"""

    @staticmethod
    def to_http_error(
        error: SyncademicError,
    ) -> tuple[https_fn.FunctionsErrorCode, str]:
        """Maps domain exceptions to Firebase Functions error codes and messages."""

        match error:
            case BaseAuthorizationError():
                return (https_fn.FunctionsErrorCode.UNAUTHENTICATED, str(error))

            case TargetCalendarNotFoundError() | SyncProfileNotFoundError():
                return (https_fn.FunctionsErrorCode.NOT_FOUND, str(error))

            case TargetCalendarAccessError():
                return (https_fn.FunctionsErrorCode.PERMISSION_DENIED, str(error))

            case DailySyncLimitExceededError():
                return (https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED, str(error))

            case IcsUrlError():
                return (https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(error))

            case SyncInProgressError():
                return (https_fn.FunctionsErrorCode.FAILED_PRECONDITION, str(error))

            case InvalidAuthCodeError():
                return (https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(error))

            case TokenVerificationError():
                return (https_fn.FunctionsErrorCode.UNAUTHENTICATED, str(error))

            case RulesetValidationError():
                return (https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(error))

            case RulesetGenerationError():
                return (https_fn.FunctionsErrorCode.INTERNAL, str(error))

            case _:
                return (https_fn.FunctionsErrorCode.INTERNAL, str(error))
