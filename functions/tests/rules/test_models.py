import pytest
from pydantic import ValidationError
from src.rules.models import (
    ChangeColorAction,
    ChangeFieldAction,
    CompoundCondition,
    CompoundConditionLogicalOperator,
    DeleteEventAction,
    EventTextField,
    Rule,
    Ruleset,
    TextFieldCondition,
    TextFieldConditionOperator,
)
from src.shared.google_calendar_colors import GoogleEventColor

from functions.tests.rules.constants import RulesSettings

settings = RulesSettings()


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


@pytest.mark.parametrize("field", ["title", "description", "location"])
def test_text_field_condition_valid_fields(field):
    condition = TextFieldCondition(
        field=field,  # type: ignore
        operator="contains",
        value="Lecture",
    )
    assert condition.field == field


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


def test_text_field_condition_empty_value():
    with pytest.raises(ValidationError) as exc_info:
        TextFieldCondition(
            field="title",
            operator="contains",
            value="",
        )
    assert "should have at least 1 character" in str(exc_info.value)


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


@pytest.mark.parametrize("operator", CompoundConditionLogicalOperator.__args__)
@pytest.mark.parametrize("length", [0, 1])
def test_invalid_compound_condition_missing_conditions(operator, length):
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )

    with pytest.raises(ValidationError):
        CompoundCondition(
            logical_operator=operator,  # type: ignore
            conditions=[condition] * length,
        )


# Test Actions
def test_change_field_action_valid():
    action = ChangeFieldAction(
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
        value=GoogleEventColor.SAGE,
    )
    assert action.action == "change_color"
    assert action.value == GoogleEventColor.SAGE


def test_change_color_action_invalid_value():
    with pytest.raises(ValidationError):
        ChangeColorAction(
            value="INVALID_COLOR",  # type: ignore
        )


def test_delete_event_action_valid():
    action = DeleteEventAction()
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


def test_rule_min_actions():
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="HAI507I",
    )
    with pytest.raises(ValidationError) as exc_info:
        Rule(
            condition=condition,
            actions=[],
        )
    assert "should have at least 1" in str(exc_info.value)


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


def test_ruleset_min_rules():
    with pytest.raises(ValidationError) as exc_info:
        Ruleset(
            rules=[],
        )
    assert "should have at least 1" in str(exc_info.value)


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


######################
### Security tests ###
######################


def long_string(length):
    """Helper function to generate a long string"""
    return "a" * length


@pytest.mark.parametrize("field", EventTextField.__args__)
@pytest.mark.parametrize("operator", TextFieldConditionOperator.__args__)
def test_text_field_condition_value_length_limit(field, operator):
    valid_value = long_string(settings.MAX_TEXT_FIELD_VALUE_LENGTH)
    condition = TextFieldCondition(
        field=field,
        operator=operator,
        value=valid_value,
    )
    assert condition.value == valid_value

    invalid_value = long_string(settings.MAX_TEXT_FIELD_VALUE_LENGTH + 1)
    with pytest.raises(ValidationError) as exc_info:
        TextFieldCondition(
            field="title",
            operator=operator,
            value=invalid_value,
        )
    assert "should have at most" in str(exc_info.value)


# Test TextFieldCondition Invalid Regex Pattern
def test_text_field_condition_invalid_regex_pattern():
    invalid_pattern = "[unclosed_group"
    with pytest.raises(ValidationError) as exc_info:
        TextFieldCondition(
            field="title",
            operator="regex",
            value=invalid_pattern,
        )
    assert "Invalid regular expression" in str(exc_info.value)


# Test CompoundCondition Maximum Number of Conditions
@pytest.mark.parametrize("logical_operator", CompoundConditionLogicalOperator.__args__)
def test_compound_condition_max_conditions(
    logical_operator: CompoundConditionLogicalOperator,
):
    valid_conditions = [
        TextFieldCondition(
            field="title",
            operator="contains",
            value=f"Lecture {i}",
        )
        for i in range(settings.MAX_CONDITIONS)
    ]
    compound_condition = CompoundCondition(
        logical_operator=logical_operator,
        conditions=valid_conditions,
    )
    assert len(compound_condition.conditions) == settings.MAX_CONDITIONS

    invalid_conditions = valid_conditions + [
        TextFieldCondition(
            field="title",
            operator="contains",
            value="Extra Lecture",
        )
    ]
    with pytest.raises(ValidationError) as exc_info:
        CompoundCondition(
            logical_operator=logical_operator,
            conditions=invalid_conditions,
        )
    assert "should have at most" in str(exc_info.value)


# # Test CompoundCondition Maximum Nesting Depth
def test_compound_condition_max_nesting_depth():
    # Function to create nested compound conditions
    def create_nested_condition(depth: int):
        condition = TextFieldCondition(
            field="title",
            operator="contains",
            value="Lecture",
        )
        for _ in range(depth):
            condition = CompoundCondition(
                logical_operator="AND",
                conditions=[condition, condition],
            )
        return condition

    # Valid nesting
    valid_condition = create_nested_condition(settings.MAX_NESTING_DEPTH + 1)
    assert valid_condition

    # Invalid nesting
    with pytest.raises(ValueError) as exc_info:
        create_nested_condition(settings.MAX_NESTING_DEPTH + 2)
    assert "Maximum nesting depth exceeded." in str(exc_info.value)


# Test ChangeFieldAction Value Length Limit
def test_change_field_action_value_length_limit():
    valid_value = long_string(settings.MAX_TEXT_FIELD_VALUE_LENGTH)
    action = ChangeFieldAction(
        action="change_field",
        field="title",
        method="append",
        value=valid_value,
    )
    assert action.value == valid_value

    invalid_value = long_string(settings.MAX_TEXT_FIELD_VALUE_LENGTH + 1)
    with pytest.raises(ValidationError) as exc_info:
        ChangeFieldAction(
            action="change_field",
            field="title",
            method="append",
            value=invalid_value,
        )
    assert "String should have at most" in str(exc_info.value)


# Test Rule Maximum Number of Actions
def test_rule_max_number_of_actions():
    valid_actions = [
        ChangeFieldAction(
            action="change_field",
            field="title",
            method="append",
            value=f"Suffix {i}",
        )
        for i in range(settings.MAX_ACTIONS)
    ]
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )
    rule = Rule(
        condition=condition,
        actions=valid_actions,
    )
    assert len(rule.actions) == settings.MAX_ACTIONS

    invalid_actions = valid_actions + [
        ChangeColorAction(
            action="change_color",
            value=GoogleEventColor.SAGE,
        )
    ]
    with pytest.raises(ValidationError) as exc_info:
        Rule(
            condition=condition,
            actions=invalid_actions,
        )
    assert "should have at most" in str(exc_info.value)


# Test Ruleset Maximum Number of Rules
def test_ruleset_max_rules():
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
    )
    action = ChangeFieldAction(
        action="change_field",
        field="title",
        method="append",
        value=" - Suffix",
    )
    valid_rules = [
        Rule(
            condition=condition,
            actions=[action],
        )
        for _ in range(settings.MAX_RULES)
    ]
    ruleset = Ruleset(
        rules=valid_rules,
    )
    assert len(ruleset.rules) == settings.MAX_RULES

    invalid_rules = valid_rules + [
        Rule(
            condition=condition,
            actions=[action],
        )
    ]
    with pytest.raises(ValidationError) as exc_info:
        Ruleset(
            rules=invalid_rules,
        )
    assert "should have at most" in str(exc_info.value)


# # Test Safe Regex Library Usage (Assuming re2 is used)
# def test_safe_regex_library_prevents_redos():
#     import re2 as re  # Assuming re2 is used

#     condition = TextFieldCondition(
#         field="title",
#         operator="regex",
#         value="(a+)+" * 10,  # Nested quantifiers to attempt ReDoS
#     )
#     event = Event(
#         title="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
#         description="Description",
#         location="Room 101",
#         start_time=None,
#         end_time=None,
#     )
#     # Should not hang or raise exception
#     result = condition.evaluate(event)
#     assert isinstance(result, bool)
