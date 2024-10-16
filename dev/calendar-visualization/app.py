from functions.ai.time_schedule_compresser import TimeScheduleCompressor
from pydantic import ValidationError
import streamlit as st
from functions.shared.event import Event
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.rules.models import Ruleset
from streamlit_calendar import calendar

st.set_page_config(
    layout="wide",
    page_title="Calendar and Rules Visualization",
)


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
    if "events" in st.session_state:
        if st.button("🗑️ Clear events", use_container_width=True):
            st.session_state.pop("events")
            st.rerun()
        st.divider()
    else:
        with st.form(key="ics_form"):
            ics_url = st.text_input(
                "Enter ICS URL",
                value=st.session_state.get("ics_url", ""),
            )
            if st.form_submit_button(label="Submit"):
                events = load_events_from_url(ics_url)
                st.session_state.ics_url = ics_url
                st.session_state.events = events
                st.success(f"Loaded {len(events)} events from ICS")

    if "events" in st.session_state and st.session_state.events:
        with st.form(key="rules_form"):
            ruleset_json = st.text_area(
                "Enter Ruleset",
                height=400,
                value=st.session_state.get("ruleset_json", ""),
            )
            if st.form_submit_button(label="🔧 Apply rules", use_container_width=True):
                try:
                    ruleset = Ruleset.model_validate_json(ruleset_json)
                except ValidationError as e:
                    st.error(e)
                else:
                    st.session_state.ruleset_json = ruleset_json
                    st.session_state.ruleset = ruleset
                    st.success("Ruleset loaded")

if "events" not in st.session_state:
    st.info("Please load events from an ICS file")
    st.stop()

visualization_tab, compression_tab = st.tabs(["Visualization", "Compression"])

with visualization_tab:
    if "events" in st.session_state:
        apply_rules = True

        if apply_rules and "ruleset" in st.session_state:
            ruleset = st.session_state.ruleset
            assert isinstance(ruleset, Ruleset)
            events = ruleset.apply(st.session_state.events)
        else:
            events = st.session_state.events

        calendar_events = [event_to_calendar_event(event) for event in events]

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

with compression_tab:
    if "events" in st.session_state:
        events = st.session_state.events
        compressed_schedule = TimeScheduleCompressor().compress(events)
        st.code(compressed_schedule)
