from firebase_functions import https_fn
from .base import SyncademicError
from .target_calendar import (
    TargetCalendarAccessError,
    TargetCalendarNotFoundError,
)
from .sync import (
    SyncInProgressError,
    SyncProfileNotFoundError,
    DailySyncLimitExceededError,
)
from .auth import BaseAuthorizationError, ProviderUserIdMismatchError, UnauthorizedError
from .ruleset import RulesetGenerationError, RulesetValidationError

from .ics import IcsSourceError


class ErrorMapping:
    """Maps domain exceptions to Firebase Functions error codes"""

    @staticmethod
    def to_http_error(error: SyncademicError) -> https_fn.HttpsError:
        """Maps domain exceptions to Firebase Functions HttpsError"""

        status_code, message = ErrorMapping.to_status_code_and_message(error)
        return https_fn.HttpsError(status_code, message)

    @staticmethod
    def to_status_code_and_message(
        error: SyncademicError,
    ) -> tuple[https_fn.FunctionsErrorCode, str]:
        """Maps domain exceptions to Firebase Functions error codes and messages."""

        match error:
            case UnauthorizedError():
                return (https_fn.FunctionsErrorCode.UNAUTHENTICATED, str(error))
            case ProviderUserIdMismatchError():
                return (https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(error))
            case BaseAuthorizationError():
                return (https_fn.FunctionsErrorCode.UNAUTHENTICATED, str(error))

            case TargetCalendarNotFoundError() | SyncProfileNotFoundError():
                return (https_fn.FunctionsErrorCode.NOT_FOUND, str(error))

            case TargetCalendarAccessError():
                return (https_fn.FunctionsErrorCode.PERMISSION_DENIED, str(error))

            case DailySyncLimitExceededError():
                return (https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED, str(error))

            case IcsSourceError():
                return (https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(error))

            case SyncInProgressError():
                return (https_fn.FunctionsErrorCode.FAILED_PRECONDITION, str(error))

            case RulesetValidationError():
                return (https_fn.FunctionsErrorCode.INVALID_ARGUMENT, str(error))

            case RulesetGenerationError():
                return (https_fn.FunctionsErrorCode.INTERNAL, str(error))

            case _:
                return (https_fn.FunctionsErrorCode.INTERNAL, str(error))

    @staticmethod
    def to_http_status_and_detail(error: SyncademicError) -> tuple[int, str]:
        code, message = ErrorMapping.to_status_code_and_message(error)
        status_map = {
            https_fn.FunctionsErrorCode.UNAUTHENTICATED: 401,
            https_fn.FunctionsErrorCode.INVALID_ARGUMENT: 400,
            https_fn.FunctionsErrorCode.NOT_FOUND: 404,
            https_fn.FunctionsErrorCode.PERMISSION_DENIED: 403,
            https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED: 429,
            https_fn.FunctionsErrorCode.FAILED_PRECONDITION: 412,
            https_fn.FunctionsErrorCode.INTERNAL: 500,
        }
        status = status_map.get(code, 500)
        return status, message
