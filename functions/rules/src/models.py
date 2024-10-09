from enum import Enum
from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field


class GoogleEventColor(str, Enum):
    """Represents the colors used in google calendar"""

    # don't use auto() here because it might cause issues with serialization/deserialization
    # e.g if we use auto() and then change the order of the enum values, the deserialization will break
    LAVENDER = "lavender"
    SAGE = "sage"
    GRAPE = "grape"
    TANGERINE = "tangerine"
    BANANA = "banana"
    FLAMINGO = "flamingo"
    PEACOCK = "peacock"
    GRAPHITE = "graphite"
    BLUEBERRY = "blueberry"
    BASIL = "basil"
    TOMATO = "tomato"

    @staticmethod
    def from_color_id(color_id: str) -> "GoogleEventColor":
        if not color_id or not color_id.isdigit() or int(color_id) not in range(1, 12):
            raise ValueError(f"Invalid color id: {color_id}")

        color_map = {
            "1": GoogleEventColor.LAVENDER,
            "2": GoogleEventColor.SAGE,
            "3": GoogleEventColor.GRAPE,
            "4": GoogleEventColor.TANGERINE,
            "5": GoogleEventColor.BANANA,
            "6": GoogleEventColor.FLAMINGO,
            "7": GoogleEventColor.PEACOCK,
            "8": GoogleEventColor.GRAPHITE,
            "9": GoogleEventColor.BLUEBERRY,
            "10": GoogleEventColor.BASIL,
            "11": GoogleEventColor.TOMATO,
        }
        return color_map[color_id]

    def to_color_code(self) -> str:
        m = {
            "1": "a4bdfc",
            "2": "7ae7bf",
            "3": "dbadff",
            "4": "ff887c",
            "5": "fbd75b",
            "6": "ffb878",
            "7": "46d6db",
            "8": "e1e1e1",
            "9": "5484ed",
            "10": "51b749",
            "11": "dc2127",
        }
        return m[self.value]


class TextFieldCondition(BaseModel):
    field: Literal["title", "description", "location"]
    operator: Literal["equals", "contains", "starts_with", "ends_with", "regex"]
    value: str
    case_sensitive: Optional[bool] = True
    negate: Optional[bool] = False


class CompoundCondition(BaseModel):
    logical_operator: Literal["AND", "OR"]
    # conditions: conlist(["ConditionType"], min_length=2)
    conditions: List["ConditionType"] = Field(..., min_length=2)

    # validate that the list of conditions is not empty -


ConditionType = Union[TextFieldCondition, CompoundCondition]

CompoundCondition.model_rebuild()


class ChangeFieldAction(BaseModel):
    action: Literal["change_field"]
    field: str
    method: Literal["set", "append", "prepend"]
    value: str


class ChangeColorAction(BaseModel):
    action: Literal["change_color"]
    value: GoogleEventColor


class DeleteEventAction(BaseModel):
    action: Literal["delete_event"]


ActionType = Union[ChangeFieldAction, ChangeColorAction, DeleteEventAction]


class Rule(BaseModel):
    condition: ConditionType
    actions: List[ActionType]


class Ruleset(BaseModel):
    rules: List[Rule]


# https://chatgpt.com/c/6704f3c6-6544-8008-844f-3bbff6df7a37
