from dataclasses import replace
import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from functions.synchronizer.synchronizer import perform_synchronization
from functions.synchronizer.ics_source import UrlIcsSource
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_cache import IcsFileStorage
from functions.synchronizer.google_calendar_manager import GoogleCalendarManager
from functions.shared.event import Event
from functions.rules.models import (
    DeleteEventAction,
    Ruleset,
    Rule,
    TextFieldCondition,
    ChangeFieldAction,
)
import arrow


past_event = Event(
    start=arrow.now().shift(days=-1),
    end=arrow.now().shift(days=-1, hours=1),
    title="Past Event",
    description="Description",
    location="Location",
)

future_event = Event(
    start=arrow.now().shift(days=1),
    end=arrow.now().shift(days=1, hours=1),
    title="Future Event",
    description="Description",
    location="Location",
)


def test_perform_manual_synchronization_successful():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"  # Assuming 'manual' is a valid value for SyncTrigger

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    now = datetime.now(timezone.utc)

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        separation_dt=now,
    )

    # Assert
    ics_source.get_ics_string.assert_called_once()
    ics_parser.parse.assert_called_once_with(ics_str)
    ics_cache.save_to_cache.assert_called_once_with(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_str=ics_str,
    )
    calendar_manager.get_events_ids_from_sync_profile.assert_called_once_with(
        sync_profile_id,
        now,
    )
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])
    calendar_manager.create_events.assert_called_once_with(
        [future_event], sync_profile_id
    )


def test_perform_scheduled_synchronization_successful():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "scheduled"  # Assuming 'manual' is a valid value for SyncTrigger

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    now = datetime.now(timezone.utc)

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        separation_dt=now,
    )

    # Assert
    ics_source.get_ics_string.assert_called_once()
    ics_parser.parse.assert_called_once_with(ics_str)
    ics_cache.save_to_cache.assert_called_once_with(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_str=ics_str,
    )
    calendar_manager.get_events_ids_from_sync_profile.assert_called_once_with(
        sync_profile_id,
        now,
    )
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])
    calendar_manager.create_events.assert_called_once_with(
        [future_event], sync_profile_id
    )


def test_perform_synchronization_with_middlewares():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Middleware that changes the event title
    def middleware(events: list[Event]) -> list[Event]:
        return [
            Event(
                start=event.start,
                end=event.end,
                title="Modified Title",
                description=event.description,
                location=event.location,
                color=event.color,
            )
            for event in events
        ]

    middlewares = [middleware]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        middlewares=middlewares,
    )

    # Assert
    ics_source.get_ics_string.assert_called_once()
    ics_parser.parse.assert_called_once_with(ics_str)
    modified_event = replace(future_event, title="Modified Title")
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])
    calendar_manager.create_events.assert_called_once_with(
        [modified_event], sync_profile_id
    )


def test_perform_synchronization_with_ruleset():
    _past_event = replace(past_event, title="Lecture")
    _future_event = replace(future_event, title="Lecture")

    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [_past_event, _future_event]

    # Define a rule that changes the title if it contains 'Lecture'
    condition = TextFieldCondition(field="title", operator="contains", value="Lecture")
    action = ChangeFieldAction(
        action="change_field", field="title", method="set", value="Modified Lecture"
    )
    rule = Rule(condition=condition, actions=[action])
    ruleset = Ruleset(rules=[rule])

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        rule_set=ruleset,
    )

    # Assert
    modified_event = replace(future_event, title="Modified Lecture")
    calendar_manager.create_events.assert_called_once_with(
        [modified_event], sync_profile_id
    )
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])


def test_perform_synchronization_no_events_after_middlewares():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Middleware that removes all events
    def middleware(events: list[Event]) -> list[Event]:
        return []

    middlewares = [middleware]

    # Mock other dependencies
    ics_cache = Mock(spec=IcsFileStorage)
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        middlewares=middlewares,
    )

    # Assert
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])
    calendar_manager.create_events.assert_not_called()


def test_perform_synchronization_no_events_after_ruleset():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Define a rule that removes all events
    condition = TextFieldCondition(field="title", operator="contains", value="Event")
    action = DeleteEventAction()
    rule = Rule(condition=condition, actions=[action])
    ruleset = Ruleset(rules=[rule])

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        rule_set=ruleset,
    )

    # Assert
    calendar_manager.create_events.assert_not_called()
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])


def test_perform_synchronization_on_create():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "on_create"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Mock other dependencies
    ics_cache = Mock(spec=IcsFileStorage)
    calendar_manager = Mock(spec=GoogleCalendarManager)

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
    )

    # Assert
    # should bypass deletion, as there's nothing to delete
    calendar_manager.get_events_ids_from_sync_profile.assert_not_called()
    calendar_manager.delete_events.assert_not_called()

    # Should event include events from the past
    calendar_manager.create_events.assert_called_once_with(
        [past_event, future_event], sync_profile_id
    )


def test_perform_synchronization_both_middlewares_and_ruleset():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mocks (details omitted for brevity)
    ics_source = Mock(spec=UrlIcsSource)
    ics_parser = Mock(spec=IcsParser)
    ics_cache = Mock(spec=IcsFileStorage)
    calendar_manager = Mock(spec=GoogleCalendarManager)

    # Middleware and Ruleset
    middlewares = [lambda events: events]
    ruleset = Ruleset(
        rules=[
            Rule(
                condition=TextFieldCondition(
                    field="title", operator="contains", value="Event"
                ),
                actions=[DeleteEventAction()],
            )
        ]
    )

    # Act & Assert
    with pytest.raises(
        AssertionError, match="Only one of middlewares or ruleset can be provided"
    ):
        perform_synchronization(
            sync_profile_id=sync_profile_id,
            sync_trigger=sync_trigger,
            ics_source=ics_source,
            ics_parser=ics_parser,
            ics_cache=ics_cache,
            calendar_manager=calendar_manager,
            middlewares=middlewares,
            rule_set=ruleset,
        )


def test_perform_synchronization_save_to_cache_exception():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)
    ics_cache.save_to_cache.side_effect = Exception("Failed to save to cache")

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["future_event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
    )

    # Assert that the synchronization continues despite the exception
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])
    calendar_manager.create_events.assert_called_once_with(
        [future_event], sync_profile_id
    )


def test_perform_manual_synchronization_full_sync():
    """
    Test manual synchronization with 'full' sync type.
    Both past and future events should be synchronized.
    """
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    # Assume both past and future events are currently in the calendar
    calendar_manager.get_events_ids_from_sync_profile.return_value = [
        "past_event_id",
        "future_event_id",
    ]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        sync_type="full",
    )

    # Assert
    ics_source.get_ics_string.assert_called_once()
    ics_parser.parse.assert_called_once_with(ics_str)
    ics_cache.save_to_cache.assert_called_once_with(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_str=ics_str,
    )
    # For 'full' sync, min_dt should be None
    calendar_manager.get_events_ids_from_sync_profile.assert_called_once_with(
        sync_profile_id,
        min_dt=None,
    )
    calendar_manager.delete_events.assert_called_once_with(
        ["past_event_id", "future_event_id"]
    )
    calendar_manager.create_events.assert_called_once_with(
        [past_event, future_event], sync_profile_id
    )


def test_perform_scheduled_synchronization_full_sync():
    """
    Test scheduled synchronization with 'full' sync type.
    Both past and future events should be synchronized.
    """
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "scheduled"

    # Mock ICS source
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [past_event, future_event]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = [
        "past_event_id",
        "future_event_id",
    ]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        sync_type="full",
    )

    # Assert
    calendar_manager.get_events_ids_from_sync_profile.assert_called_once_with(
        sync_profile_id,
        min_dt=None,
    )
    calendar_manager.delete_events.assert_called_once_with(
        ["past_event_id", "future_event_id"]
    )
    calendar_manager.create_events.assert_called_once_with(
        [past_event, future_event], sync_profile_id
    )


def test_perform_synchronization_with_middlewares_full_sync():
    """
    Test synchronization with middlewares applied, using 'full' sync type.
    """
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_parser = Mock(spec=IcsParser)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str
    ics_parser.parse.return_value = [past_event, future_event]

    # Middleware that modifies event titles
    def middleware(events: list[Event]) -> list[Event]:
        return [replace(event, title="Modified Title") for event in events]

    middlewares = [middleware]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = [
        "past_event_id",
        "future_event_id",
    ]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        middlewares=middlewares,
        sync_type="full",
    )

    # Assert
    modified_past_event = replace(past_event, title="Modified Title")
    modified_future_event = replace(future_event, title="Modified Title")
    calendar_manager.create_events.assert_called_once_with(
        [modified_past_event, modified_future_event], sync_profile_id
    )


def test_perform_synchronization_with_ruleset_full_sync():
    """
    Test synchronization with a ruleset applied, using 'full' sync type.
    """
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Events with titles to match condition
    _past_event = replace(past_event, title="Lecture")
    _future_event = replace(future_event, title="Lecture")

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_parser = Mock(spec=IcsParser)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str
    ics_parser.parse.return_value = [_past_event, _future_event]

    # Define rule to change title
    condition = TextFieldCondition(field="title", operator="contains", value="Lecture")
    action = ChangeFieldAction(
        action="change_field", field="title", method="set", value="Modified Lecture"
    )
    rule = Rule(condition=condition, actions=[action])
    ruleset = Ruleset(rules=[rule])

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = [
        "past_event_id",
        "future_event_id",
    ]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        rule_set=ruleset,
        sync_type="full",
    )

    # Assert
    modified_past_event = replace(_past_event, title="Modified Lecture")
    modified_future_event = replace(_future_event, title="Modified Lecture")
    calendar_manager.create_events.assert_called_once_with(
        [modified_past_event, modified_future_event], sync_profile_id
    )
    calendar_manager.delete_events.assert_called_once_with(
        ["past_event_id", "future_event_id"]
    )
