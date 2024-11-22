import re
from functions.ai.ruleset_builder import RulesetBuilder
from functions.ai.types import RulesetOutput
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

load_dotenv("../../functions/.env.syncademic-36c18")

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
    if "events" in st.session_state:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.pop("ics_string")
            st.session_state.pop("events", None)
            st.session_state.pop("compressed_schedule", None)
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
def get_llm(model: str) -> BaseChatModel:
    return init_chat_model(model)


# Function to display the compressed schedule
def display_compressed_schedule(events: list[Event]):
    compressed_schedule = TimeScheduleCompressor().compress(events)
    st.session_state.compressed_schedule = compressed_schedule
    st.code(compressed_schedule)


# Function to remove names from a text
def remove_names_from_text(text: str):
    with get_openai_callback() as cb:
        llm = get_llm("gpt-4o-mini")
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
visualization_tab, ics_content_tab, compression_tab, pii_remover_tab, ai_rules_tab = (
    st.tabs(["Visualization", "ICS Content", "Compression", "PII Remover", "AI Rules"])
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


# Function to generate ruleset from compressed schedule
def generate_ruleset_from_schedule(
    compressed_schedule: str, *, llm_model: str = "gpt-4o"
):
    llm = get_llm(llm_model)
    ruleset_builder = RulesetBuilder(llm=llm)
    try:
        with st.spinner("Generating ruleset..."):
            ruleset = ruleset_builder.generate_ruleset(compressed_schedule)
        st.session_state.ruleset_output = ruleset
        st.session_state.ruleset = ruleset.ruleset
    except Exception as e:
        st.error(f"Failed to generate ruleset: {e}")


# AI Rules Tab
with ai_rules_tab:
    if "compressed_schedule" in st.session_state:
        llm_model = st.selectbox("Select LLM Model", ["gpt-4o", "gpt-4o-mini"])

        if st.button("🧠 Generate Ruleset"):
            generate_ruleset_from_schedule(
                st.session_state.compressed_schedule,
                llm_model=llm_model,
            )

        if "ruleset_output" in st.session_state:
            output = st.session_state.ruleset_output
            assert isinstance(output, RulesetOutput)
            st.write(output.brainstorming)
            st.divider()
            st.subheader("Ruleset: ")

            st.code(output.model_dump_json(indent=2), language="json")

    else:
        st.error(
            "No compressed schedule available. Please compress the schedule first."
        )
