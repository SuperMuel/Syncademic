import re
from dataclasses import replace
from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field
from src.shared.event import Event
from src.shared.google_calendar_colors import GoogleEventColor


class TextFieldCondition(BaseModel):
    field: Literal["title", "description", "location"]
    operator: Literal["equals", "contains", "starts_with", "ends_with", "regex"]
    value: str
    case_sensitive: Optional[bool] = True
    negate: Optional[bool] = False

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

        return not result if self.negate else result


class CompoundCondition(BaseModel):
    logical_operator: Literal["AND", "OR"]
    conditions: List["ConditionType"] = Field(..., min_length=2)

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
    action: Literal["change_field"]
    field: Literal["title", "description", "location"]
    method: Literal["set", "append", "prepend"]
    value: str

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

        return replace(event, **{self.field: new_field_value})


class ChangeColorAction(BaseModel):
    action: Literal["change_color"]
    value: GoogleEventColor

    def apply(self, event: Event) -> Optional[Event]:
        return replace(event, color=self.value)


class DeleteEventAction(BaseModel):
    action: Literal["delete_event"]

    def apply(self, event: Event) -> Optional[Event]:
        return None


ActionType = Union[ChangeFieldAction, ChangeColorAction, DeleteEventAction]


class Rule(BaseModel):
    condition: ConditionType
    actions: List[ActionType]

    def apply(self, event: Event) -> Optional[Event]:
        if self.condition.evaluate(event):
            for action in self.actions:
                result = action.apply(event)
                if result is None:
                    return None
                event = result
        return event


class Ruleset(BaseModel):
    rules: List[Rule]

    def apply(self, events: List[Event]) -> List[Event]:
        new_events = []
        for event in events:
            for rule in self.rules:
                event = rule.apply(event)
                if event is None:
                    break
            if event is not None:
                new_events.append(event)
        return new_events


# https://chatgpt.com/c/6704f3c6-6544-8008-844f-3bbff6df7a37
