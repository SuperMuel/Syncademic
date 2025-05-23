from datetime import datetime
from typing import Any, TypedDict

import streamlit as st
from streamlit_calendar import calendar
from backend.shared.event import Event
from backend.models.rules import Ruleset


class EventDisplayData(TypedDict):
    """Type for event display data in a dataframe"""

    start: datetime
    end: datetime
    title: str
    description: str | None
    location: str | None
    color: str | None


def event_to_display_data(event: Event) -> EventDisplayData:
    """Convert an Event to display data for a dataframe"""
    return {
        "start": event.start.datetime,
        "end": event.end.datetime,
        "title": event.title,
        "description": event.description,
        "location": event.location,
        "color": event.color.value if event.color else None,
    }


def apply_rules(events: list[Event], ruleset: Ruleset | None = None) -> list[Event]:
    """Apply a ruleset to a list of events"""
    if not ruleset:
        return events

    print(f"Applying {len(events)} events with {len(ruleset.rules)} rules")

    after = ruleset.apply(events)

    if not after:
        st.warning("No events remain after applying rules")

    return after


def display_events_dataframe(events: list[Event]) -> None:
    """Display events in a Streamlit dataframe

    Args:
        events: List of events to display
    """

    # Convert events to display format
    display_data = [event_to_display_data(event) for event in events]

    # Display events
    st.dataframe(
        display_data,
        column_config={
            "start": st.column_config.DatetimeColumn(
                "Start Time",
                help="Event start time",
                format="DD/MM/YY HH:mm",
            ),
            "end": st.column_config.DatetimeColumn(
                "End Time",
                help="Event end time",
                format="DD/MM/YY HH:mm",
            ),
            "title": st.column_config.TextColumn(
                "Title",
                help="Event title",
                width="large",
            ),
            "description": st.column_config.TextColumn(
                "Description",
                help="Event description",
                width="large",
            ),
            "location": st.column_config.TextColumn(
                "Location",
                help="Event location",
                width="medium",
            ),
            "color": st.column_config.TextColumn(
                "Color",
                help="Event color",
                width="small",
            ),
        },
        use_container_width=True,
    )


def display_events_calendar(
    events: list[Event],
    key: str | None = None,
) -> Any:
    """Display events in a Streamlit calendar, optionally applying a ruleset

    Args:
        events: List of events to display
        ruleset: Optional ruleset to apply to events before display

    Returns:
        Whatever the streamlit-calendar widget returns
    """
    if not events:
        st.warning("No events to display")
        return None

    calendar_events = [
        {
            "title": event.title,
            # Convert to ISO-8601 strings:
            "start": event.start.datetime.isoformat(),
            "end": event.end.datetime.isoformat(),
            # Set color from event.color if available, otherwise use grey
            "backgroundColor": event.color.to_color_code()
            if event.color
            else "#808080",
            "borderColor": event.color.to_color_code() if event.color else "#808080",
            "extendedProps": {
                "location": event.location,
                "description": event.description,
            },
        }
        for event in events
    ]

    # Example FullCalendar config (see the streamlit-calendar docs for more)
    calendar_options = {
        "initialView": "timeGridWeek",
        "editable": False,
        "selectable": False,
        "headerToolbar": {
            "start": "prev,next today",
            "center": "title",
            "end": "timeGridWeek,dayGridMonth",
        },
        "firstDay": 1,
        # "initialDate": To set if today's date falls outside of the time schedule range
    }

    # custom_css = """
    #     .fc-event-title {
    #         font-weight: bold;
    #     }
    # """

    return calendar(
        events=calendar_events,
        options=calendar_options,
        # custom_css=custom_css,  # optional
        key=key,  # unique widget key to maintain state
    )
