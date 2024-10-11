import arrow
from src.shared.event import Event
from src.shared.google_calendar_colors import GoogleEventColor
from src.rules.models import (
    ChangeColorAction,
    ChangeFieldAction,
    CompoundCondition,
    DeleteEventAction,
    Rule,
    Ruleset,
    TextFieldCondition,
)

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
