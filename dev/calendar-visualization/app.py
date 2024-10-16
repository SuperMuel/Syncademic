from functions.shared.google_calendar_colors import GoogleEventColor
import streamlit as st
from functions.shared.event import Event
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from streamlit_calendar import calendar

st.set_page_config(layout="wide")


def load_events_from_url(url: str) -> list[Event]:
    loader = UrlIcsSource(url)
    return IcsParser().parse(loader.get_ics_string())


def event_to_calendar_event(event: Event) -> dict:
    # https://fullcalendar.io/docs/event-object
    d = {
        "title": event.title,
        "start": event.start.isoformat(),
        "end": event.end.isoformat(),
    }

    if event.color:
        d["backgroundColor"] = event.color.to_color_code()

    return d


with st.sidebar:
    with st.form(key="ics_form"):
        ics_url = st.text_input("Enter ICS URL")
        if st.form_submit_button(label="Submit"):
            events = load_events_from_url(ics_url)
            st.session_state.events = events
            st.success(f"Loaded {len(events)} events from ICS")

if "events" in st.session_state:
    calendar_events = [
        event_to_calendar_event(event) for event in st.session_state.events
    ]

    calendar_options = {
        "editable": "false",
        "selectable": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "timeGridWeek",
        },
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": "timeGridWeek",
    }

    # Display the calendar with events
    calendar_display = calendar(
        events=calendar_events,
        options=calendar_options,
    )
    # st.write(calendar_display)
