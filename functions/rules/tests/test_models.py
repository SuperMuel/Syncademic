from pydantic import ValidationError
import pytest

from shared.google_calendar_colors import GoogleEventColor
from src.models import (
    ChangeColorAction,
    ChangeFieldAction,
    CompoundCondition,
    DeleteEventAction,
    Rule,
    Ruleset,
    TextFieldCondition,
)


def test_text_field_condition_valid():
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
        case_sensitive=False,
        negate=False,
    )
    assert condition.field == "title"
    assert condition.operator == "contains"
    assert condition.value == "Lecture"
    assert condition.case_sensitive == False  # noqa: E712
    assert condition.negate == False  # noqa: E712


def test_text_field_condition_valid_regex():
    condition = TextFieldCondition(
        field="title",
        operator="regex",
        value="^Lecture.*",
        case_sensitive=False,
        negate=False,
    )
    assert condition.field == "title"
    assert condition.operator == "regex"
    assert condition.value == "^Lecture.*"
    assert condition.case_sensitive == False  # noqa: E712
    assert condition.negate == False  # noqa: E712


def test_text_field_condition_valid_fields():
    for valid_field in ["title", "description", "location"]:
        condition = TextFieldCondition(
            field=valid_field,  # type: ignore
            operator="contains",
            value="Lecture",
        )
        assert condition.field == valid_field


def test_text_field_condition_invalid_field():
    with pytest.raises(ValidationError):
        TextFieldCondition(
            field="invalid_field",  # type: ignore
            operator="contains",
            value="Lecture",
        )


def test_text_field_condition_invalid_operator():
    with pytest.raises(ValidationError):
        TextFieldCondition(
            field="title",
            operator="invalid_operator",  # type:ignore
            value="Lecture",
        )


def test_text_field_condition_missing_fields():
    with pytest.raises(ValidationError) as exc_info:
        TextFieldCondition(
            operator="contains",
            value="Lecture",
        )  # type: ignore
    assert "field\n  Field required" in str(exc_info.value)


# Test CompoundCondition
def test_compound_condition_valid():
    condition1 = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )
    condition2 = TextFieldCondition(
        field="description",
        operator="equals",
        value="Math",
    )
    compound_condition = CompoundCondition(
        logical_operator="AND", conditions=[condition1, condition2]
    )
    assert compound_condition.logical_operator == "AND"
    assert len(compound_condition.conditions) == 2
    assert compound_condition.conditions[0] == condition1
    assert compound_condition.conditions[1] == condition2


def test_compound_condition_invalid_logical_operator():
    condition1 = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )
    with pytest.raises(ValidationError):
        CompoundCondition(
            logical_operator="some operator",  # type: ignore
            conditions=[condition1],
        )


# Test Actions
def test_change_field_action_valid():
    action = ChangeFieldAction(
        action="change_field",
        field="title",
        method="prepend",
        value="Calcul formel - ",
    )
    assert action.action == "change_field"
    assert action.field == "title"
    assert action.method == "prepend"
    assert action.value == "Calcul formel - "


def test_change_field_action_invalid_action():
    with pytest.raises(ValidationError):
        ChangeFieldAction(
            action="invalid_action",  # type: ignore
            field="title",
            method="prepend",
            value="Calcul formel - ",
        )


def test_change_color_action_valid():
    action = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )
    assert action.action == "change_color"
    assert action.value == GoogleEventColor.SAGE


def test_change_color_action_invalid_value():
    with pytest.raises(ValidationError):
        ChangeColorAction(
            action="change_color",
            value="INVALID_COLOR",  # type: ignore
        )


def test_delete_event_action_valid():
    action = DeleteEventAction(
        action="delete_event",
    )
    assert action.action == "delete_event"


def test_delete_event_action_invalid_action():
    with pytest.raises(ValidationError):
        DeleteEventAction(
            action="invalid_action",  # type: ignore
        )


# Test Rule
def test_rule_valid():
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="HAI507I",
        case_sensitive=False,
        negate=False,
    )
    action1 = ChangeFieldAction(
        action="change_field",
        field="title",
        method="prepend",
        value="Calcul formel - ",
    )
    action2 = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )
    rule = Rule(
        condition=condition,
        actions=[action1, action2],
    )
    assert rule.condition == condition
    assert len(rule.actions) == 2
    assert rule.actions[0] == action1
    assert rule.actions[1] == action2


# Test Ruleset
def test_ruleset_valid():
    condition1 = TextFieldCondition(
        field="title",
        operator="contains",
        value="HAI507I",
    )
    action1 = ChangeFieldAction(
        action="change_field",
        field="title",
        method="prepend",
        value="Calcul formel - ",
    )
    rule1 = Rule(
        condition=condition1,
        actions=[action1],
    )

    condition2 = CompoundCondition(
        logical_operator="OR",
        conditions=[
            TextFieldCondition(
                field="title",
                operator="contains",
                value="HAX503X",
            ),
            TextFieldCondition(
                field="title",
                operator="contains",
                value="HAX505X",
            ),
        ],
    )
    action2 = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.TOMATO,
    )
    rule2 = Rule(
        condition=condition2,
        actions=[action2],
    )

    ruleset = Ruleset(
        rules=[rule1, rule2],
    )

    assert len(ruleset.rules) == 2
    assert ruleset.rules[0] == rule1
    assert ruleset.rules[1] == rule2


# Test Serialization and Deserialization
def test_serialization():
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="HAI507I",
        case_sensitive=False,
        negate=False,
    )
    action1 = ChangeFieldAction(
        action="change_field",
        field="title",
        method="prepend",
        value="Calcul formel - ",
    )
    action2 = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )
    rule = Rule(
        condition=condition,
        actions=[action1, action2],
    )
    ruleset = Ruleset(
        rules=[rule],
    )
    json_data = ruleset.model_dump_json()
    assert isinstance(json_data, str)

    # Deserialize and compare
    parsed_ruleset = Ruleset.model_validate_json(json_data)
    assert parsed_ruleset == ruleset


def test_change_color_action_serialization():
    action = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )
    json_data = action.model_dump_json()

    # Deserialize
    action_parsed = ChangeColorAction.model_validate_json(json_data)
    assert action_parsed.value == GoogleEventColor.SAGE


def test_rule_from_invalid_json():
    rule_json = """
    {
        "condition": {
            "field": "title",
            "operator": "contains",
            "value": "HAI507I"
        },
        "actions": [
            {
                "action": "change_field",
                "field": "title",
                "method": "invalid_method",
                "value": "Calcul formel - "
            }
        ]
    }
    """
    with pytest.raises(ValidationError):
        Rule.model_validate_json(rule_json)


def test_nested_compound_condition():
    condition1 = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )
    condition2 = TextFieldCondition(
        field="description",
        operator="equals",
        value="Math",
    )
    compound_condition_inner = CompoundCondition(
        logical_operator="AND", conditions=[condition1, condition2]
    )

    condition3 = TextFieldCondition(
        field="location",
        operator="equals",
        value="Room 101",
    )
    compound_condition_outer = CompoundCondition(
        logical_operator="OR", conditions=[compound_condition_inner, condition3]
    )

    assert compound_condition_outer.logical_operator == "OR"
    assert len(compound_condition_outer.conditions) == 2
    assert compound_condition_outer.conditions[0] == compound_condition_inner
    assert compound_condition_outer.conditions[1] == condition3


def test_color_enum_serialization_contains_name():
    action = ChangeColorAction(action="change_color", value=GoogleEventColor.TANGERINE)
    json_data = action.model_dump_json()

    # Rules are written by AI or human, so they need to be human/AI-readable
    assert "tangerine" in json_data.lower()


# Additional tests for validation and error handling


def test_invalid_compound_condition_missing_conditions():
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )

    for length in [0, 1]:
        for operator in ["AND", "OR"]:
            with pytest.raises(ValidationError):
                CompoundCondition(
                    logical_operator=operator,  # type: ignore
                    conditions=[condition] * length,
                )
