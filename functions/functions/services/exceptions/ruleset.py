from .base import SyncademicError


class BaseRulesetError(SyncademicError):
    """Base class for ruleset-related errors"""

    pass


class RulesetGenerationError(BaseRulesetError):
    """Raised when AI fails to generate rules"""

    pass


class RulesetValidationError(BaseRulesetError):
    """Raised when generated rules fail validation"""

    pass
