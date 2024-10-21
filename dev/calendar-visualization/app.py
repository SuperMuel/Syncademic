from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from pii.pii_identifier import funny_teacher_names
import re
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import init_chat_model
from pydantic import ValidationError
import streamlit as st
from functions.shared.event import Event
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource
from functions.rules.models import Ruleset
from streamlit_calendar import calendar
from pii.pii_identifier import extract_names

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    layout="wide",
    page_title="Calendar and Rules Visualization",
)


def load_events_from_url(url: str) -> list[Event]:
    """Load events from an ICS URL."""
    loader = UrlIcsSource(url)
    return IcsParser().parse(loader.get_ics_string())


def event_to_calendar_event(event: Event) -> dict:
    """Convert an Event object into a format compatible with FullCalendar."""
    d = {
        "title": event.title,
        "start": event.start.isoformat(),
        "end": event.end.isoformat(),
    }

    if event.color:
        d["backgroundColor"] = event.color.to_color_code()

    return d


def clear_events():
    """Clear loaded events from the session state."""
    if "events" in st.session_state:
        if st.button("🗑️ Clear events", use_container_width=True):
            st.session_state.pop("events")
            st.rerun()
        st.divider()


def load_events_form():
    """Display a form for loading events from an ICS URL."""
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


def load_ruleset_form():
    """Display a form for loading a ruleset."""
    with st.form(key="rules_form"):
        ruleset_json = st.text_area(
            "Enter Ruleset",
            height=400,
            value=st.session_state.get("ruleset_json", ""),
        )
        if st.form_submit_button(label="🔧 Apply rules", use_container_width=True):
            if not ruleset_json:
                st.session_state.pop("ruleset", None)
            else:
                try:
                    ruleset = Ruleset.model_validate_json(ruleset_json)
                except ValidationError as e:
                    st.error(e)
                else:
                    st.session_state.ruleset_json = ruleset_json
                    st.session_state.ruleset = ruleset
                    st.success("Ruleset loaded")


def display_calendar(events: list[Event], ruleset: Ruleset | None = None):
    """Display the calendar with events, applying rules if provided."""
    if ruleset:
        events = ruleset.apply(events)

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
        "firstDay": 1,
        "initialDate": events[0].start.date().isoformat(),
    }

    calendar(
        events=calendar_events,
        options=calendar_options,
    )


@st.cache_resource
def get_llm() -> BaseChatModel:
    return init_chat_model("gpt-4o-mini")


# a function that proposes a button to replace names found in the text with fictional names
def show_replace_names_button(text: str, names: list[str]):
    """Displays a button that when clicked will replace names in the text with fictional names."""

    if st.button("👤 Replace names"):
        replaced_text = text
        for name, teacher in zip(names, funny_teacher_names):
            # use regex to replace the name even if the name doesn't respect the case
            replaced_text = re.sub(
                rf"\b{name}\b", teacher, replaced_text, flags=re.IGNORECASE
            )

        st.code(replaced_text)


def display_names_finder(compressed_schedule: str):
    """Displays a button that when clicked will display any person names from the compressed schedule."""
    assert compressed_schedule, "Compressed schedule must not be empty"

    # return extract_names(compressed_schedule, get_llm())

    if st.button("🕵️ Find names"):
        with st.spinner("Extracting names..."):
            names = extract_names(compressed_schedule, get_llm())

        if names:
            st.session_state.names = [name.name for name in names]
        else:
            st.write("No names found")

    if "names" not in st.session_state:
        return

    # write names as a df
    st.write("Found names:")
    st.write(st.session_state.names)

    show_replace_names_button(compressed_schedule, st.session_state.names)


def display_compressed_schedule(events: list[Event]):
    """Display the compressed schedule for the given events."""
    compressed_schedule = TimeScheduleCompressor().compress(events)
    st.session_state.compressed_schedule = compressed_schedule
    st.code(compressed_schedule)

    display_names_finder(compressed_schedule)


# Main Streamlit Sidebar Logic
with st.sidebar:
    clear_events()

    if "events" not in st.session_state:
        load_events_form()
    elif st.session_state.events:
        load_ruleset_form()

# Main Streamlit Content Logic
if "events" not in st.session_state:
    st.info("Please load events from an ICS file")
    st.stop()

visualization_tab, compression_tab = st.tabs(["Visualization", "Compression"])

# Visualization Tab
with visualization_tab:
    events = st.session_state.events
    ruleset = st.session_state.get("ruleset")
    display_calendar(events, ruleset)

# Compression Tab
with compression_tab:
    display_compressed_schedule(st.session_state.events)
