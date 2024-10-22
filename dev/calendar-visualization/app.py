import re

import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel
from langchain_community.callbacks import get_openai_callback
from pii.pii_identifier import (
    create_fictional_names,
    extract_names,
)
from streamlit_calendar import calendar

from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from functions.rules.models import Ruleset
from functions.shared.event import Event
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource

load_dotenv()

st.set_page_config(
    layout="wide",
    page_title="Calendar and Rules Visualization",
)


# Helper function to load events from an ICS string
def load_events_from_string(ics_string: str) -> list[Event]:
    return IcsParser().parse(ics_string)


# Function to convert Event to calendar-compatible format
def event_to_calendar_event(event: Event) -> dict:
    d = {
        "title": event.title,
        "start": event.start.isoformat(),
        "end": event.end.isoformat(),
    }
    if event.color:
        d["backgroundColor"] = event.color.to_color_code()
    return d


# Function to clear ICS data
def clear_ics_data():
    if "ics_string" in st.session_state:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.pop("ics_string")
            st.session_state.pop("ics_url", None)
            st.session_state.pop("events", None)
            st.rerun()


# Function to load events form
def load_events_form():
    with st.form(key="ics_form"):
        ics_url = st.text_input(
            "Enter ICS URL", value=st.session_state.get("ics_url", "")
        )
        ics_file = st.file_uploader("Upload ICS file", type=["ics"])

        if st.form_submit_button(label="Submit", use_container_width=True):
            if ics_file:
                ics_string = ics_file.read().decode("utf-8")
                st.session_state.ics_string = ics_string
                st.session_state.events = load_events_from_string(ics_string)
                st.success(
                    f"Loaded {len(st.session_state.events)} events from uploaded file"
                )
            elif ics_url:
                loader = UrlIcsSource(ics_url)
                ics_string = loader.get_ics_string()
                st.session_state.ics_url = ics_url
                st.session_state.ics_string = ics_string
                st.session_state.events = load_events_from_string(ics_string)
                st.success(f"Loaded {len(st.session_state.events)} events from URL")
            else:
                st.warning("Please provide either an ICS URL or upload a file.")


# Function to display calendar
def display_calendar(events: list[Event], ruleset: Ruleset | None = None):
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

    calendar(events=calendar_events, options=calendar_options)


# Cache the LLM resource
@st.cache_resource
def get_llm() -> BaseChatModel:
    return init_chat_model("gpt-4o-mini")


# Function to display the compressed schedule
def display_compressed_schedule(events: list[Event]):
    compressed_schedule = TimeScheduleCompressor().compress(events)
    st.session_state.compressed_schedule = compressed_schedule
    st.code(compressed_schedule)


# Function to remove names from a text
def remove_names_from_text(text: str):
    with get_openai_callback() as cb:
        llm = get_llm()
        with st.spinner("Extracting names..."):
            real_names = extract_names(text, llm)

        if not real_names:
            st.write("No names found")
            return

        real_names_col, fictional_names_col = st.columns(2)

        with real_names_col:
            st.session_state.names_to_remove = [name.name for name in real_names]
            st.subheader("Found names:")
            st.write(st.session_state.names_to_remove)

        with fictional_names_col:
            with st.spinner("Creating fictional names..."):
                fictional_names = create_fictional_names(
                    llm, st.session_state.names_to_remove
                )

            st.subheader("Fictional names:")
            st.write([name.fictional_name for name in fictional_names.replacements])

    st.write(cb)

    if len(st.session_state.names_to_remove) != len(fictional_names.replacements):
        st.warning(
            f"There was {len(st.session_state.names_to_remove)} names found, but only {len(fictional_names.replacements)} fictional names were created. Please try again."
        )
        return

    anonymized_text = text
    fictional_names = [name.fictional_name for name in fictional_names.replacements]
    for name, fictional in zip(st.session_state.names_to_remove, fictional_names):
        anonymized_text = re.sub(
            rf"\b{name}\b", fictional, anonymized_text, flags=re.IGNORECASE
        )

    # Check if the text contains any real names
    compiled_names = [
        re.compile(rf"\b{name}\b", re.IGNORECASE)
        for name in st.session_state.names_to_remove
    ]
    for name_regex in compiled_names:
        if name_regex.search(anonymized_text):
            st.warning(f"Failed to anonymize {name_regex.pattern}. Please try again.")
            return

    st.subheader("Anonymized Text:")
    st.code(anonymized_text)


# Sidebar logic for ICS management
with st.sidebar:
    clear_ics_data()
    if "ics_string" not in st.session_state:
        load_events_form()

# Main content with tabs for different functionalities
visualization_tab, ics_content_tab, compression_tab, pii_remover_tab = st.tabs(
    ["Visualization", "ICS Content", "Compression", "PII Remover"]
)

# ICS Content Tab
with ics_content_tab:
    if "ics_string" in st.session_state:
        st.code(st.session_state.ics_string)
    else:
        st.error("No ICS content available. Please load an ICS file.")

# Visualization Tab
with visualization_tab:
    if "events" in st.session_state:
        events = st.session_state.events
        ruleset = st.session_state.get("ruleset", None)
        display_calendar(events, ruleset)
    else:
        st.error("No events to visualize. Please load an ICS file.")

# Compression Tab
with compression_tab:
    if "events" in st.session_state:
        display_compressed_schedule(st.session_state.events)
    else:
        st.error("No events to compress. Please load an ICS file.")

# PII Remover Tab
with pii_remover_tab:
    text_input = st.text_area("Enter text to anonymize", height=400)
    if st.button("🕵️ Detect and Remove Names"):
        if text_input.strip():
            remove_names_from_text(text_input)
        else:
            st.warning("Please enter some text.")


# from functions.ai.time_schedule_compressor import TimeScheduleCompressor
# from pii.pii_identifier import funny_teacher_names
# import re
# from langchain.chat_models.base import BaseChatModel
# from langchain.chat_models import init_chat_model
# from pydantic import ValidationError
# import streamlit as st
# from functions.shared.event import Event
# from functions.synchronizer.ics_parser import IcsParser
# from functions.synchronizer.ics_source import UrlIcsSource
# from functions.rules.models import Ruleset
# from streamlit_calendar import calendar
# from pii.pii_identifier import extract_names

# from dotenv import load_dotenv

# load_dotenv()

# st.set_page_config(
#     layout="wide",
#     page_title="Calendar and Rules Visualization",
# )


# def load_events_from_url(url: str) -> list[Event]:
#     """Load events from an ICS URL."""
#     loader = UrlIcsSource(url)
#     return IcsParser().parse(loader.get_ics_string())


# def event_to_calendar_event(event: Event) -> dict:
#     """Convert an Event object into a format compatible with FullCalendar."""
#     d = {
#         "title": event.title,
#         "start": event.start.isoformat(),
#         "end": event.end.isoformat(),
#     }

#     if event.color:
#         d["backgroundColor"] = event.color.to_color_code()

#     return d


# def clear_events():
#     """Clear loaded events from the session state."""
#     if "events" in st.session_state:
#         if st.button("🗑️ Clear events", use_container_width=True):
#             st.session_state.pop("events")
#             st.rerun()
#         st.divider()


# def load_events_form():
#     """Display a form for loading events from an ICS URL."""
#     with st.form(key="ics_form"):
#         ics_url = st.text_input(
#             "Enter ICS URL",
#             value=st.session_state.get("ics_url", ""),
#         )
#         if st.form_submit_button(label="Submit"):
#             events = load_events_from_url(ics_url)
#             st.session_state.ics_url = ics_url
#             st.session_state.events = events
#             st.success(f"Loaded {len(events)} events from ICS")


# def load_ruleset_form():
#     """Display a form for loading a ruleset."""
#     with st.form(key="rules_form"):
#         ruleset_json = st.text_area(
#             "Enter Ruleset",
#             height=400,
#             value=st.session_state.get("ruleset_json", ""),
#         )
#         if st.form_submit_button(label="🔧 Apply rules", use_container_width=True):
#             if not ruleset_json:
#                 st.session_state.pop("ruleset", None)
#             else:
#                 try:
#                     ruleset = Ruleset.model_validate_json(ruleset_json)
#                 except ValidationError as e:
#                     st.error(e)
#                 else:
#                     st.session_state.ruleset_json = ruleset_json
#                     st.session_state.ruleset = ruleset
#                     st.success("Ruleset loaded")


# def display_calendar(events: list[Event], ruleset: Ruleset | None = None):
#     """Display the calendar with events, applying rules if provided."""
#     if ruleset:
#         events = ruleset.apply(events)

#     calendar_events = [event_to_calendar_event(event) for event in events]
#     calendar_options = {
#         "editable": "false",
#         "selectable": "true",
#         "headerToolbar": {
#             "left": "today prev,next",
#             "center": "title",
#             "right": "timeGridWeek",
#         },
#         "slotMinTime": "06:00:00",
#         "slotMaxTime": "18:00:00",
#         "initialView": "timeGridWeek",
#         "firstDay": 1,
#         "initialDate": events[0].start.date().isoformat(),
#     }

#     calendar(
#         events=calendar_events,
#         options=calendar_options,
#     )


# @st.cache_resource
# def get_llm() -> BaseChatModel:
#     return init_chat_model("gpt-4o-mini")


# # a function that proposes a button to replace names found in the text with fictional names
# def show_replace_names_button(text: str, names: list[str]):
#     """Displays a button that when clicked will replace names in the text with fictional names."""

#     if st.button("👤 Replace names"):
#         replaced_text = text
#         for name, teacher in zip(names, funny_teacher_names):
#             # use regex to replace the name even if the name doesn't respect the case
#             replaced_text = re.sub(
#                 rf"\b{name}\b", teacher, replaced_text, flags=re.IGNORECASE
#             )

#         st.code(replaced_text)


# def display_names_finder(compressed_schedule: str):
#     """Displays a button that when clicked will display any person names from the compressed schedule."""
#     assert compressed_schedule, "Compressed schedule must not be empty"

#     # return extract_names(compressed_schedule, get_llm())

#     if st.button("🕵️ Find names"):
#         with st.spinner("Extracting names..."):
#             names = extract_names(compressed_schedule, get_llm())

#         if names:
#             st.session_state.names = [name.name for name in names]
#         else:
#             st.write("No names found")

#     if "names" not in st.session_state:
#         return

#     # write names as a df
#     st.write("Found names:")
#     st.write(st.session_state.names)

#     show_replace_names_button(compressed_schedule, st.session_state.names)


# def display_compressed_schedule(events: list[Event]):
#     """Display the compressed schedule for the given events."""
#     compressed_schedule = TimeScheduleCompressor().compress(events)
#     st.session_state.compressed_schedule = compressed_schedule
#     st.code(compressed_schedule)

#     display_names_finder(compressed_schedule)


# # Main Streamlit Sidebar Logic
# with st.sidebar:
#     clear_events()

#     if "events" not in st.session_state:
#         load_events_form()
#     elif st.session_state.events:
#         load_ruleset_form()


# def stop_if_no_events():
#     if "events" not in st.session_state:
#         st.info("Please load events from an ICS file")
#         st.stop()


# visualization_tab, compression_tab, pii_remover_tab = st.tabs(
#     [
#         "Visualization",
#         "Compression",
#         "PII Remover",
#     ]
# )

# # Visualization Tab
# with visualization_tab:
#     if "events" in st.session_state:
#         events = st.session_state.events
#         ruleset = st.session_state.get("ruleset")
#         display_calendar(events, ruleset)
#     else:
#         st.error("Load events to visualize them.")

# # Compression Tab
# with compression_tab:
#     if "events" in st.session_state:
#         display_compressed_schedule(st.session_state.events)
#     else:
#         st.error("Load events to compress them.")


# with pii_remover_tab:
#     # Input for the text where names need to be removed
#     text_input = st.text_area(
#         "Enter text to anonymize",
#         height=400,
#         value=st.session_state.get("pii_text", ""),
#     )

#     if st.button("🕵️ Detect and Remove Names"):
#         if not text_input.strip():
#             st.warning("Please enter some text.")
#         else:
#             with st.spinner("Detecting names..."):
#                 names = extract_names(text_input, get_llm())

#             if names:
#                 st.session_state.names_to_remove = [name.name for name in names]
#                 st.session_state.pii_text = text_input
#                 st.success(
#                     f"Found {len(names)} names: {', '.join(st.session_state.names_to_remove)}"
#                 )
#             else:
#                 st.warning("No names found in the provided text.")

#     # If names were detected, display the button to anonymize the text
#     if "names_to_remove" in st.session_state:
#         anonymized_text = text_input
#         for name in st.session_state.names_to_remove:
#             # Replace each found name with "REDACTED" or any other placeholder
#             anonymized_text = re.sub(
#                 rf"\b{name}\b", "REDACTED", anonymized_text, flags=re.IGNORECASE
#             )

#         st.subheader("Anonymized Text:")
#         st.code(anonymized_text)
