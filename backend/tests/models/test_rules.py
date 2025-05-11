import arrow
import pytest
from pydantic import ValidationError

from backend.models import (
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
from backend.models.rules import settings
from backend.shared.event import Event
from backend.shared.google_calendar_colors import GoogleEventColor


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


########################
### Evaluation tests ###
########################


start = arrow.get("2022-01-01T12:00:00")
end = arrow.get("2022-01-01T13:00:00")


def test_text_field_condition_evaluate():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    # Condition: title contains "507I", case-insensitive
    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="507i",
        case_sensitive=False,
    )

    assert condition.evaluate(event) is True

    # Condition: title starts with "Lecture"
    condition = TextFieldCondition(
        field="title",
        operator="starts_with",
        value="Lecture",
    )

    assert condition.evaluate(event) is False

    # Condition: description equals "Calcul formel"
    condition = TextFieldCondition(
        field="description",
        operator="equals",
        value="Calcul formel",
    )

    assert condition.evaluate(event) is True

    # Condition: location ends with "101"
    condition = TextFieldCondition(
        field="location",
        operator="ends_with",
        value="101",
    )

    assert condition.evaluate(event) is True

    # Condition: regex match on title
    condition = TextFieldCondition(
        field="title",
        operator="regex",
        value=r"HAI\d+I",
    )

    assert condition.evaluate(event) is True


def test_negate():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
        negate=False,
    )

    assert condition.evaluate(event) is True

    condition = TextFieldCondition(
        field="title",
        operator="contains",
        value="Lecture",
        negate=True,
    )

    assert condition.evaluate(event) is False


def test_case_sensitive():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    case_sensitive_condition = TextFieldCondition(
        field="description",
        operator="contains",
        value="calcul",
        case_sensitive=True,
    )

    assert case_sensitive_condition.evaluate(event) is False

    case_insensitive_condition = TextFieldCondition(
        field="description",
        operator="contains",
        value="calcul",
        case_sensitive=False,
    )

    assert case_insensitive_condition.evaluate(event) is True


def test_compound_condition_evaluate():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    condition1 = TextFieldCondition(
        field="title",
        operator="contains",
        value="HAI507I",
    )
    condition2 = TextFieldCondition(
        field="description",
        operator="contains",
        value="formel",
    )

    compound_condition = CompoundCondition(
        logical_operator="AND",
        conditions=[condition1, condition2],
    )

    assert compound_condition.evaluate(event) is True

    condition3 = TextFieldCondition(
        field="location",
        operator="equals",
        value="Room 202",
    )

    compound_condition_or = CompoundCondition(
        logical_operator="OR",
        conditions=[condition1, condition3],
    )

    assert compound_condition_or.evaluate(event) is True

    # Test with a condition that should fail
    condition4 = TextFieldCondition(
        field="description",
        operator="equals",
        value="Algebra",
    )

    compound_condition_and = CompoundCondition(
        logical_operator="AND",
        conditions=[condition1, condition4],
    )

    assert compound_condition_and.evaluate(event) is False


def test_change_field_action_apply():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    action = ChangeFieldAction(
        action="change_field",
        field="title",
        method="prepend",
        value="Calcul formel - ",
    )

    new_event = action.apply(event)

    assert new_event is not None
    assert new_event.title == "Calcul formel - HAI507I Lecture"
    assert new_event.description == event.description
    assert new_event.location == event.location


def test_change_field_action_cut_after():
    event = Event(
        title="Séminaire de rentrée - EFALYO 3 Gpe C",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    action = ChangeFieldAction(
        action="change_field",
        field="title",
        method="cut-after",
        value=" - EFALYO",
    )

    new_event = action.apply(event)

    assert new_event is not None
    assert new_event.title == "Séminaire de rentrée"

    # Test when value is not found
    event2 = Event(
        title="Pure title",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )
    new_event2 = action.apply(event2)
    assert new_event2 is not None
    assert new_event2.title == "Pure title"


def test_change_field_action_cut_before():
    event = Event(
        title="Séminaire de rentrée - EFALYO 3 Gpe C",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    action = ChangeFieldAction(
        action="change_field",
        field="title",
        method="cut-before",
        value="EFALYO",
    )

    new_event = action.apply(event)

    assert new_event is not None
    assert new_event.title == " 3 Gpe C"

    # Test when value is not found
    event2 = Event(
        title="Pure title",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )
    new_event2 = action.apply(event2)
    assert new_event2 is not None
    assert new_event2.title == "Pure title"


def test_change_color_action_apply():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        color=None,
        start=start,
        end=end,
    )

    action = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )

    new_event = action.apply(event)

    assert new_event is not None
    assert new_event.color == GoogleEventColor.SAGE
    assert new_event.title == event.title


def test_delete_event_action_apply():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )

    action = DeleteEventAction(
        action="delete_event",
    )

    new_event = action.apply(event)

    assert new_event is None


def test_rule_apply():
    event = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        color=None,
        start=start,
        end=end,
    )

    condition = TextFieldCondition(
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

    action2 = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )

    rule = Rule(
        condition=condition,
        actions=[action1, action2],
    )

    new_event = rule.apply(event)

    assert new_event is not None
    assert new_event.title == "Calcul formel - HAI507I Lecture"
    assert new_event.color == GoogleEventColor.SAGE


def test_ruleset_apply():
    event1 = Event(
        title="HAI507I Lecture",
        description="Calcul formel",
        location="Room 101",
        start=start,
        end=end,
    )
    event2 = Event(
        title="HAX503X Lecture",
        description="Fourier Analysis",
        location="Room 202",
        start=start,
        end=end,
    )
    event3 = Event(
        title="HAX504X Seminar",
        description="Combinatorics",
        location="Room 303",
        start=start,
        end=end,
    )

    # Rule 1
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
    action2 = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.SAGE,
    )
    rule1 = Rule(
        condition=condition1,
        actions=[action1, action2],
    )

    # Rule 2
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
    action3 = ChangeFieldAction(
        action="change_field",
        field="title",
        method="prepend",
        value="Mesure et intégration, Fourier - ",
    )
    action4 = ChangeColorAction(
        action="change_color",
        value=GoogleEventColor.TOMATO,
    )
    rule2 = Rule(
        condition=condition2,
        actions=[action3, action4],
    )

    # Rule 3
    condition3 = TextFieldCondition(
        field="title",
        operator="contains",
        value="HAX504X",
    )
    action5 = DeleteEventAction(
        action="delete_event",
    )
    rule3 = Rule(
        condition=condition3,
        actions=[action5],
    )

    ruleset = Ruleset(
        rules=[rule1, rule2, rule3],
    )

    events = [event1, event2, event3]

    new_events = ruleset.apply(events)

    assert len(new_events) == 2

    new_event1 = new_events[0]
    new_event2 = new_events[1]

    assert new_event1.title == "Calcul formel - HAI507I Lecture"
    assert new_event1.color == GoogleEventColor.SAGE

    assert new_event2.title == "Mesure et intégration, Fourier - HAX503X Lecture"
    assert new_event2.color == GoogleEventColor.TOMATO
