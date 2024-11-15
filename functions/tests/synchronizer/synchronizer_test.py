from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import Mock

import arrow
import pytest

from functions.rules.models import (
    ChangeFieldAction,
    DeleteEventAction,
    Rule,
    Ruleset,
    TextFieldCondition,
)
from functions.shared.event import Event
from functions.shared.google_calendar_colors import GoogleEventColor
from functions.synchronizer.google_calendar_manager import GoogleCalendarManager
from functions.synchronizer.ics_cache import IcsFileStorage
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.synchronizer.synchronizer import perform_synchronization

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
        ruleset=ruleset,
    )

    # Assert
    modified_event = replace(
        future_event,
        title="Modified Lecture",
        color=GoogleEventColor.GRAPHITE,  # Temporary : since a ruleset is provided that will probably change colors, we will first manually set all the events to grey color
    )
    calendar_manager.create_events.assert_called_once_with(
        [modified_event], sync_profile_id
    )
    calendar_manager.delete_events.assert_called_once_with(["future_event_id"])


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
        ruleset=ruleset,
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
        ruleset=ruleset,
        sync_type="full",
    )

    # Assert
    modified_past_event = replace(
        _past_event,
        title="Modified Lecture",
        color=GoogleEventColor.GRAPHITE,  # Temporary : since a ruleset is provided that will probably change colors, we will first manually set all the events to grey color
    )
    modified_future_event = replace(
        _future_event,
        title="Modified Lecture",
        color=GoogleEventColor.GRAPHITE,  # Temporary : since a ruleset is provided that will probably change colors, we will first manually set all the events to grey color
    )
    calendar_manager.create_events.assert_called_once_with(
        [modified_past_event, modified_future_event], sync_profile_id
    )
    calendar_manager.delete_events.assert_called_once_with(
        ["past_event_id", "future_event_id"]
    )


def test_event_ending_at_separation_dt():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Create an event that ends exactly at separation_dt
    separation_dt = datetime.now(timezone.utc)
    event_ending_at_separation = Event(
        start=arrow.get(separation_dt).shift(hours=-1),
        end=arrow.get(separation_dt),  # Ends exactly at separation_dt
        title="Event Ending Now",
        description="Ends at separation_dt",
        location="Location",
    )

    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [event_ending_at_separation]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    calendar_manager.get_events_ids_from_sync_profile.return_value = []  # Google calendar do not returns events ending exactly at separation_dt

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        separation_dt=separation_dt,
        sync_type="regular",
    )

    # Assert
    # Since event.end == separation_dt, and event.end > separation_dt is False,
    # the event should NOT be included in new_events
    calendar_manager.create_events.assert_not_called()
    calendar_manager.delete_events.assert_not_called()


def test_event_starting_at_separation_dt():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Create an event that starts exactly at separation_dt
    separation_dt = datetime.now(timezone.utc)
    event_starting_at_separation = Event(
        start=arrow.get(separation_dt),  # Starts exactly at separation_dt
        end=arrow.get(separation_dt).shift(hours=1),
        title="Event Starting Now",
        description="Starts at separation_dt",
        location="Location",
    )

    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [event_starting_at_separation]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)

    # The event is returned by Google Calendar because event.end > separation_dt
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        separation_dt=separation_dt,
        sync_type="regular",
    )

    # Assert
    # Since event.end > separation_dt, the event should be included in new_events
    calendar_manager.create_events.assert_called_once_with(
        [event_starting_at_separation], sync_profile_id
    )
    # The old event should be deleted
    calendar_manager.delete_events.assert_called_once_with(["event_id"])


def test_event_spanning_separation_dt():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Create an event that starts before and ends after separation_dt
    separation_dt = datetime.now(timezone.utc)
    event_spanning_separation = Event(
        start=arrow.get(separation_dt).shift(hours=-1),
        end=arrow.get(separation_dt).shift(hours=1),
        title="Event Spanning Now",
        description="Spans over separation_dt",
        location="Location",
    )

    # ICS parser returns this event
    ics_parser = Mock(spec=IcsParser)
    ics_parser.parse.return_value = [event_spanning_separation]

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)
    # The event is returned by Google Calendar because event.end > separation_dt
    calendar_manager.get_events_ids_from_sync_profile.return_value = ["event_id"]

    # Act
    perform_synchronization(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_parser=ics_parser,
        ics_cache=ics_cache,
        calendar_manager=calendar_manager,
        separation_dt=separation_dt,
        sync_type="regular",
    )

    # Assert
    # Since event.end > separation_dt, the event should be included in new_events
    calendar_manager.create_events.assert_called_once_with(
        [event_spanning_separation], sync_profile_id
    )
    # Delete the old event
    calendar_manager.delete_events.assert_called_once_with(["event_id"])


def test_save_to_cache_on_parsing_error():
    # Arrange
    sync_profile_id = "test_sync_profile"
    sync_trigger = "manual"

    # Mock ICS source and parser
    ics_source = Mock(spec=UrlIcsSource)
    ics_str = "BEGIN:VCALENDAR\n...END:VCALENDAR"
    ics_source.get_ics_string.return_value = ics_str

    # Mock ICS parser
    ics_parser = Mock(spec=IcsParser)
    exception = Exception("Failed to parse ICS")
    ics_parser.parse.side_effect = exception

    # Mock ICS cache
    ics_cache = Mock(spec=IcsFileStorage)

    # Mock calendar manager
    calendar_manager = Mock(spec=GoogleCalendarManager)

    # Act
    with pytest.raises(Exception, match="Failed to parse ICS"):
        perform_synchronization(
            sync_profile_id=sync_profile_id,
            sync_trigger=sync_trigger,
            ics_source=ics_source,
            ics_parser=ics_parser,
            ics_cache=ics_cache,
            calendar_manager=calendar_manager,
        )

    # Assert
    ics_cache.save_to_cache.assert_called_once_with(
        sync_profile_id=sync_profile_id,
        sync_trigger=sync_trigger,
        ics_source=ics_source,
        ics_str=ics_str,
        parsing_error=exception,
    )
    calendar_manager.delete_events.assert_not_called()
    calendar_manager.create_events.assert_not_called()
