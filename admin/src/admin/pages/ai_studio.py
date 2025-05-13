from backend.infrastructure.event_bus import MockEventBus
import streamlit as st
import json
from typing import cast

# --- Admin imports ---
from admin.shared.data_service import data_service
from admin.shared.event_display import (
    apply_rules,
    display_events_calendar,
    display_events_dataframe,
)

# --- Backend/Services imports ---
from backend.ai.ruleset_builder import RulesetBuilder
from backend.ai.time_schedule_compressor import TimeScheduleCompressor
from backend.ai.types import RulesetOutput
from backend.models.rules import Ruleset
from backend.models.sync_profile import SyncProfile
from backend.services.ai_ruleset_service import AiRulesetService
from backend.services.ics_service import IcsService
from backend.shared.event import Event
from backend.services.exceptions.ics import IcsParsingError
from backend.synchronizer.ics_source import IcsSource, StringIcsSource, UrlIcsSource
from backend.synchronizer.ics_parser import IcsParser

# Initialize services
event_bus = MockEventBus()
ics_service = IcsService(event_bus=event_bus)
ruleset_builder = RulesetBuilder()
ai_ruleset_service = AiRulesetService(
    ics_service=ics_service,
    sync_profile_repo=data_service.sync_profile_repo,
    ruleset_builder=ruleset_builder,
    event_bus=event_bus,
)

# Session state initialization
if "ics_content" not in st.session_state:
    st.session_state["ics_content"] = None
if "sync_profile_id" not in st.session_state:
    st.session_state["sync_profile_id"] = None
if "ruleset" not in st.session_state:
    st.session_state.ruleset = None
if "events_before" not in st.session_state:
    st.session_state.events_before = None
if "events_after" not in st.session_state:
    st.session_state.events_after = None
if "generated_ruleset" not in st.session_state:
    st.session_state.generated_ruleset = None
if "generating_ruleset" not in st.session_state:
    st.session_state.generating_ruleset = False
if "brainstorming" not in st.session_state:
    st.session_state.brainstorming = None


@st.cache_data()
def _get_sync_profile(sync_profile_id: str) -> SyncProfile | None:
    return data_service.get_sync_profile(sync_profile_id)


@st.cache_data(
    show_spinner="Fetching ICS content...",
    hash_funcs={
        UrlIcsSource: lambda x: x.model_dump_json(),
        StringIcsSource: lambda x: x.model_dump_json(),
    },
)
def _fetch_ics(source: IcsSource):
    return source.get_ics_string()


def generate_ai_ruleset(events: list[Event]) -> Ruleset | None:
    """Generates a ruleset using the RulesetBuilder for the provided events."""
    st.session_state.generating_ruleset = True

    try:
        ruleset_output: RulesetOutput = ruleset_builder.generate_ruleset(
            events=events,
            metadata={"source": "ai_studio"},
        )

        st.session_state.ruleset = ruleset_output.ruleset
        st.session_state.generated_ruleset = ruleset_output
        st.session_state.brainstorming = ruleset_output.brainstorming
        return ruleset_output.ruleset
    except Exception as e:
        st.error(f"Error generating ruleset: {e}")
        return None
    finally:
        st.session_state.generating_ruleset = False


# ICS INPUT
with st.sidebar:
    input_method = st.radio(
        "Select ICS input method:",
        options=["Existing SyncProfile", "URL", "File", "Paste Content"],
    )

    source: IcsSource

    if input_method == "Existing SyncProfile":
        sync_profile_id = st.text_input("Sync Profile ID")
        st.session_state["sync_profile_id"] = sync_profile_id
        chosen_profile = _get_sync_profile(sync_profile_id)
        if not chosen_profile:
            st.error("SyncProfile not found.")
            st.stop()

        source = chosen_profile.scheduleSource.to_ics_source()

    elif input_method == "URL":
        ics_url = st.text_input("ICS URL")
        st.session_state["ics_url"] = ics_url
        try:
            source = UrlIcsSource.from_str(ics_url)
        except Exception as e:
            st.error(f"Invalid URL: {e}")
            st.stop()

    elif input_method == "File":
        file = st.file_uploader("Upload ICS file", type=["ics"])
        if not file:
            st.error("No file uploaded.")
            st.stop()
        source = StringIcsSource(ics_string=file.read().decode("utf-8"))

    elif input_method == "Paste Content":
        ics_content = st.text_area("ICS Content")
        if not ics_content.strip():
            st.error("No content pasted.")
            st.stop()
        source = StringIcsSource(ics_string=ics_content)

    else:
        st.error("Invalid input method.")
        st.stop()


ics_str = _fetch_ics(source)
events_or_error = IcsParser().try_parse(ics_str)

if isinstance(events_or_error, IcsParsingError):
    st.error(f"Error parsing ICS: {events_or_error}")
    st.stop()

events_before = events_or_error


### Ruleset selection
ruleset: Ruleset | None = None
with st.sidebar:
    st.subheader("Ruleset")

    sync_profile_ruleset: Ruleset | None = None
    if input_method == "Existing SyncProfile":
        sync_profile = _get_sync_profile(st.session_state["sync_profile_id"])
        assert sync_profile is not None
        if sync_profile.ruleset:
            sync_profile_ruleset = sync_profile.ruleset
        else:
            st.warning("The selected SyncProfile has no ruleset.")

    if sync_profile_ruleset:
        ruleset_choice = st.radio(
            "Which ruleset do you want to use?",
            options=[
                "The SyncProfile's ruleset",
                "A custom ruleset",
            ],
            index=0,
        )
    else:
        ruleset_choice = "A custom ruleset"

    if ruleset_choice == "The SyncProfile's ruleset":
        ruleset = sync_profile_ruleset
    elif ruleset_choice == "A custom ruleset":
        # Custom ruleset input
        custom_ruleset_json = st.text_area(
            "Ruleset JSON",
            value=st.session_state.ruleset.model_dump_json()
            if st.session_state.ruleset
            else "",
        )
        if custom_ruleset_json:
            try:
                ruleset = Ruleset.model_validate_json(custom_ruleset_json)
                st.session_state.ruleset = ruleset
            except Exception as e:
                st.error(f"Error parsing ruleset: {e}")
                st.stop()

    # Add a divider before the AI generation section
    st.divider()

    # AI Ruleset Generation Section
    st.subheader("AI Ruleset Generation")

    if st.button(
        "Generate Ruleset with AI", disabled=st.session_state.generating_ruleset
    ):
        with st.spinner("Generating ruleset..."):
            # Cast events_before to list[Event] since we already checked it's not an Exception
            events_list = cast(list[Event], events_before)
            generated_ruleset = generate_ai_ruleset(events_list)
            if generated_ruleset:
                ruleset = generated_ruleset
                st.success("Ruleset generated successfully!")
            st.rerun()

    # Show brainstorming if a ruleset was generated
    if st.session_state.brainstorming:
        with st.expander("AI Brainstorming", expanded=False):
            st.markdown(st.session_state.brainstorming)

# Create tabs for different views
tab_titles = ["Raw ICS", "Compressed View", "Raw Events"]
if ruleset:
    tab_titles.insert(2, "Ruleset")
    tab_titles.append("After Rules")
tab_titles.append("Ruleset Schema")

# Create tab objects and collect them in a dictionary
tab_objects = st.tabs(tab_titles)
tabs = {title: tab for title, tab in zip(tab_titles, tab_objects)}

# Raw ICS tab
with tabs["Raw ICS"]:
    st.code(ics_str, language=None)

# Compressed view tab
with tabs["Compressed View"]:
    compressor = TimeScheduleCompressor()
    compressed_content = compressor.compress(events_before)
    st.code(compressed_content, language=None)

# Ruleset JSON tab (if available)
if ruleset:
    with tabs["Ruleset"]:
        st.write(ruleset.model_dump())

# Events tab - show both calendar and table
with tabs["Raw Events"]:
    st.subheader("Calendar View")
    display_events_calendar(events_before, key="ai_studio_calendar_before")

    st.divider()

    st.subheader("Table View")
    display_events_dataframe(events_before)

# After Rules tab (if ruleset available)
if ruleset:
    with tabs["After Rules"]:
        events_after = apply_rules(events_before, ruleset)

        # Fix to display calendar in tabs
        # (https://github.com/im-perativa/streamlit-calendar/issues/3#issuecomment-2025927658)
        calendar_style = """
        <style>
            iframe[title="streamlit_calendar.calendar"] {
                height: 600px; 
            }
        </style>
        """
        st.markdown(calendar_style, unsafe_allow_html=True)
        # End of fix
        # After Rules tab - show both calendar and table
        st.subheader("Calendar View")
        result = display_events_calendar(events_after, key="ai_studio_calendar_after")
        st.write(result)

        st.divider()

        st.subheader("Table View")
        display_events_dataframe(events_after)

# Ruleset Schema tab (always available)
with tabs["Ruleset Schema"]:
    st.subheader("OpenAPI Schema")
    schema = Ruleset.model_json_schema()
    st.code(json.dumps(schema, indent=2), language="json")

    st.divider()

    st.subheader("About this Schema")
    st.markdown("""
    This OpenAPI schema is automatically generated from the Ruleset Pydantic model. 
    It describes the structure, field types, and validation rules of the Ruleset class.
    
    The schema follows the [OpenAPI Specification](https://swagger.io/specification/) 
    and can be used to:
    
    - Generate API documentation
    - Validate ruleset data
    - Create client SDKs for interacting with ruleset APIs
    - Understand the expected format of ruleset JSON
    """)
