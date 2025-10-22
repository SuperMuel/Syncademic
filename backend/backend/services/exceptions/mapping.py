from fastapi import status as fastapi_status
from firebase_functions import https_fn

from .auth import BaseAuthorizationError, ProviderUserIdMismatchError, UnauthorizedError
from .base import SyncademicError
from .ics import IcsSourceError
from .ruleset import RulesetGenerationError, RulesetValidationError
from .sync import (
    DailySyncLimitExceededError,
    SyncInProgressError,
    SyncProfileNotFoundError,
)
from .target_calendar import (
    TargetCalendarAccessError,
    TargetCalendarNotFoundError,
)


FIREBASE_TO_FASTAPI_STATUS: dict[https_fn.FunctionsErrorCode, int] = {
    https_fn.FunctionsErrorCode.INVALID_ARGUMENT: fastapi_status.HTTP_422_UNPROCESSABLE_ENTITY,
    https_fn.FunctionsErrorCode.UNAUTHENTICATED: fastapi_status.HTTP_401_UNAUTHORIZED,
    https_fn.FunctionsErrorCode.PERMISSION_DENIED: fastapi_status.HTTP_403_FORBIDDEN,
    https_fn.FunctionsErrorCode.NOT_FOUND: fastapi_status.HTTP_404_NOT_FOUND,
    https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED: fastapi_status.HTTP_429_TOO_MANY_REQUESTS,
    https_fn.FunctionsErrorCode.FAILED_PRECONDITION: fastapi_status.HTTP_412_PRECONDITION_FAILED,
    https_fn.FunctionsErrorCode.INTERNAL: fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR,
}


class ErrorMapping:
    """Maps domain exceptions to Firebase Functions error codes"""

    @staticmethod
    def to_http_error(error: SyncademicError) -> https_fn.HttpsError:
        """Maps domain exceptions to Firebase Functions HttpsError"""

        status_code, message = ErrorMapping.to_firebase_status_code_and_message(error)
        return https_fn.HttpsError(status_code, message)

    @staticmethod
    def to_firebase_status_code_and_message(
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
    def to_fastapi_status_code_and_message(
        error: SyncademicError,
    ) -> tuple[int, str]:
        """Maps domain exceptions to FastAPI-friendly HTTP status codes."""

        firebase_status, message = ErrorMapping.to_firebase_status_code_and_message(
            error
        )

        http_status = FIREBASE_TO_FASTAPI_STATUS.get(
            firebase_status,
            fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        return http_status, message
