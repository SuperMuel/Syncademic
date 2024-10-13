from pydantic_settings import BaseSettings


class RulesSettings(BaseSettings):
    MAX_TEXT_FIELD_VALUE_LENGTH: int = 256
    MAX_CONDITIONS: int = 10
    MAX_ACTIONS: int = 5
    MAX_RULES: int = 15
    MAX_NESTING_DEPTH: int = 5
