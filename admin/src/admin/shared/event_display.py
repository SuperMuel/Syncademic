from datetime import datetime
from typing import TypedDict

import streamlit as st
from functions.shared.event import Event
from functions.models.rules import Ruleset


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


def display_events(events: list[Event], ruleset: Ruleset | None = None) -> None:
    """Display events in a Streamlit dataframe, optionally applying a ruleset

    Args:
        events: List of events to display
        ruleset: Optional ruleset to apply to events before display
    """
    if not events:
        st.warning("No events found")
        return

    # Apply ruleset if provided
    if ruleset:
        with st.spinner("Applying rules..."):
            events = ruleset.apply(events)
            if not events:
                st.warning("No events remain after applying rules")
                return

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
