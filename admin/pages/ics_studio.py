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


def display_file_content(storage: FirebaseIcsFileStorage, filename: str) -> str:
    """Display and return the content of the ICS file."""
    file_content = storage.get_file_content(filename)
    with st.expander("Raw ICS Content"):
        st.code(file_content, language="ics")
    return file_content


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


def main() -> None:
    st.title("🐛 ICS Studio")

    # Initialize services
    ics_storage, ics_parser = initialize_services()

    # Sidebar filters form
    with st.sidebar:
        st.header("Filters")
        with st.form("ics_filters"):
            selected_profile_id = st.text_input(
                "Sync Profile ID", placeholder="Enter ID"
            )
            # Add more filters here as needed
            st.form_submit_button("Apply Filters", use_container_width=True)

    # Fetch and display files
    try:
        files = ics_storage.list_files(prefix=selected_profile_id)
    except Exception as e:
        st.error(f"Error listing files: {e}")
        st.stop()

    if not files:
        st.error("No ICS files found matching the filters.")
        st.stop()

    # Sort files by updated date (newest first)
    files = sorted(files, key=lambda x: x["updated"], reverse=True)

    # File selection
    with st.sidebar:
        selected_file = st.selectbox(
            "Select ICS File", options=files, format_func=lambda x: x["name"]
        )

        if selected_file:
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

    if not selected_file:
        st.error("Select a file to continue")
        st.stop()

    # Display file information
    display_file_details(cast(IcsFileInfo, selected_file))
    file_content = display_file_content(ics_storage, selected_file["name"])
    display_parsed_events(ics_parser, file_content)


main()
