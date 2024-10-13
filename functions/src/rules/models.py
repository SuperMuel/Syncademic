import re
from dataclasses import replace
from typing import Literal, Optional, Self, Union, Sequence

from pydantic import BaseModel, Field, model_validator

from tests.rules.constants import RulesSettings
from src.shared.event import Event
from src.shared.google_calendar_colors import GoogleEventColor

settings = RulesSettings()

EventTextField = Literal["title", "description", "location"]
TextFieldConditionOperator = Literal[
    "equals", "contains", "starts_with", "ends_with", "regex"
]


class TextFieldCondition(BaseModel):
    field: EventTextField
    operator: TextFieldConditionOperator
    value: str = Field(
        ..., min_length=1, max_length=settings.MAX_TEXT_FIELD_VALUE_LENGTH
    )
    case_sensitive: Optional[bool] = True
    negate: Optional[bool] = False

    @model_validator(mode="after")
    def validate_regex(self) -> Self:
        if self.operator == "regex":
            try:
                re.compile(self.value)
            except re.error as e:
                raise ValueError(
                    f"Invalid regular expression: `{self.value}`, error: {e}"
                )
        return self

    def evaluate(self, event: Event) -> bool:
        field_value = getattr(event, self.field)
        assert isinstance(field_value, str)

        condition_value = self.value

        if not self.case_sensitive:
            field_value = field_value.lower()
            condition_value = condition_value.lower()

        match self.operator:
            case "equals":
                result = field_value == condition_value
            case "contains":
                result = condition_value in field_value
            case "starts_with":
                result = field_value.startswith(condition_value)
            case "ends_with":
                result = field_value.endswith(condition_value)
            case "regex":
                flags = 0 if self.case_sensitive else re.IGNORECASE
                result = bool(re.search(condition_value, field_value, flags))
            case _:
                raise ValueError(f"Unimplemented operator: {self.operator}")

        return not result if self.negate else result


CompoundConditionLogicalOperator = Literal["AND", "OR"]


class CompoundCondition(BaseModel):
    logical_operator: CompoundConditionLogicalOperator
    conditions: Sequence["ConditionType"] = Field(
        ..., min_length=2, max_length=settings.MAX_CONDITIONS
    )

    @model_validator(mode="after")
    def validate_nesting_depth(self) -> Self:
        def check_depth(condition, current_depth=1):
            if isinstance(condition, CompoundCondition):
                if current_depth > settings.MAX_NESTING_DEPTH:
                    raise ValueError("Maximum nesting depth exceeded.")
                for cond in condition.conditions:
                    check_depth(cond, current_depth + 1)

        for condition in self.conditions:
            check_depth(condition)

        return self

    def evaluate(self, event: Event) -> bool:
        match self.logical_operator:
            case "AND":
                return all(condition.evaluate(event) for condition in self.conditions)
            case "OR":
                return any(condition.evaluate(event) for condition in self.conditions)

        raise ValueError(f"Unimplemented logical operator: {self.logical_operator}")


ConditionType = Union[TextFieldCondition, CompoundCondition]

CompoundCondition.model_rebuild()


class ChangeFieldAction(BaseModel):
    action: Literal["change_field"] = "change_field"
    field: EventTextField
    method: Literal["set", "append", "prepend"]
    value: str = Field(
        ..., min_length=0, max_length=settings.MAX_TEXT_FIELD_VALUE_LENGTH
    )

    def apply(self, event: Event) -> Optional[Event]:
        field_value = getattr(event, self.field)
        assert isinstance(field_value, str)

        new_value = self.value

        match self.method:
            case "set":
                new_field_value = new_value
            case "append":
                new_field_value = field_value + new_value
            case "prepend":
                new_field_value = new_value + field_value
            case _:
                raise ValueError(f"Unimplemented method: {self.method}")

        return replace(event, **{self.field: new_field_value})


class ChangeColorAction(BaseModel):
    action: Literal["change_color"] = "change_color"
    value: GoogleEventColor

    def apply(self, event: Event) -> Optional[Event]:
        return replace(event, color=self.value)


class DeleteEventAction(BaseModel):
    action: Literal["delete_event"] = "delete_event"

    def apply(self, event: Event) -> Optional[Event]:
        return None


ActionType = ChangeFieldAction | ChangeColorAction | DeleteEventAction


class Rule(BaseModel):
    condition: ConditionType
    actions: Sequence[ActionType] = Field(
        ..., min_length=1, max_length=settings.MAX_ACTIONS
    )

    def apply(self, event: Event) -> Optional[Event]:
        if self.condition.evaluate(event):
            for action in self.actions:
                result = action.apply(event)
                if result is None:
                    return None
                event = result
        return event


class Ruleset(BaseModel):
    rules: Sequence[Rule] = Field(..., min_length=1, max_length=settings.MAX_RULES)

    def apply(self, events: Sequence[Event]) -> list[Event]:
        new_events = []
        for event in events:
            for rule in self.rules:
                event = rule.apply(event)
                if event is None:
                    break
            if event is not None:
                new_events.append(event)
        return new_events
