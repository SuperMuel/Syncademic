import os
import streamlit as st
from firebase_admin import storage
from datetime import datetime
from typing import TypedDict, cast

from functions.services.exceptions.ics import IcsParsingError
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser


class IcsFileInfo(TypedDict):
    name: str
    updated: datetime
    metadata: dict


@st.cache_resource
def initialize_services() -> tuple[FirebaseIcsFileStorage, IcsParser]:
    """Initialize and return required services."""
    ics_storage = FirebaseIcsFileStorage(
        bucket=storage.bucket(os.getenv("STORAGE_BUCKET"))
    )
    ics_parser = IcsParser()
    return ics_storage, ics_parser


def display_file_details(file: IcsFileInfo) -> None:
    """Display details of the selected ICS file."""
    st.subheader("File Details")
    col1, col2 = st.columns(2)
    col1.write(f"**Filename:** {file['name']}")
    col2.write(f"**Last Updated:** {file['updated'].strftime('%Y-%m-%d %H:%M:%S')}")
    st.json(file["metadata"])


def display_file_content(file_content: str) -> None:
    """Display and return the content of the ICS file."""
    if not file_content:
        return st.error("No content found for the selected file.")
    with st.expander("Raw ICS Content"):
        st.code(file_content, language="ics")


def display_parsed_events(parser: IcsParser, content: str) -> None:
    """Parse and display events from the ICS content."""
    with st.expander("Parsed Events"):
        events = parser.try_parse(content)
        if isinstance(events, IcsParsingError):
            st.error(f"Error parsing ICS file: {events}")
            return

        event_data = [
            {
                "Start Time": event.start,
                "End Time": event.end,
                "Summary": event.title,
                "Description": event.description,
                "Location": event.location,
            }
            for event in events
        ]
        st.dataframe(event_data, use_container_width=True)


st.title("🐛 ICS Studio")

# Initialize services
ics_storage, ics_parser = initialize_services()


@st.cache_data
def get_all_files() -> list[dict]:
    return ics_storage.list_files()


all_files = get_all_files()

# Sidebar filters form
with st.sidebar:
    st.header("Filters")
    with st.form("search_form"):
        str_search = st.text_input("String Search")
        # Add more filters here as needed
        st.form_submit_button("Apply Filters", use_container_width=True)

# Fetch and display files
try:
    filtered_files = all_files
    if str_search:
        filtered_files = [
            file for file in filtered_files if str_search.lower() in str(file).lower()
        ]

except Exception as e:
    st.error(f"Error listing files: {e}")
    st.stop()

if not filtered_files:
    st.error("No ICS files found matching the filters.")
    st.stop()

# Sort files by updated date (newest first)
filtered_files = sorted(filtered_files, key=lambda x: x["updated"], reverse=True)

with st.expander("All Files"):
    st.write(filtered_files)

# File selection
with st.sidebar:
    selected_file = st.selectbox(
        "Select ICS File", options=filtered_files, format_func=lambda x: x["name"]
    )

    if not selected_file:
        st.error("Select a file to continue")
        st.stop()

    # Download button
    file_content = ics_storage.get_file_content(selected_file["name"])
    st.download_button(
        "Download ICS File",
        data=file_content,
        file_name=selected_file["name"],
        mime="text/calendar",
        use_container_width=True,
        icon="📥",
    )

display_file_details(cast(IcsFileInfo, selected_file))
display_file_content(file_content)
display_parsed_events(ics_parser, file_content)
