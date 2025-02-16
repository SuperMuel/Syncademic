import os
import streamlit as st
from firebase_admin import storage

from functions.services.exceptions.ics import IcsParsingError
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage
from functions.synchronizer.ics_parser import IcsParser

st.title("🐛 ICS Studio")

# Initialize services
ics_storage = FirebaseIcsFileStorage(bucket=storage.bucket(os.getenv("STORAGE_BUCKET")))
ics_parser = IcsParser()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filters")
    selected_profile_id = st.text_input("Sync Profile ID", placeholder="Enter ID")
    # Add more filters as needed (date range, user ID, etc.)

# --- List ICS Files ---
st.header("Cached ICS Files")

# Fetch file list
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

# Create a selectbox for file selection
selected_file_name = st.sidebar.selectbox(
    "Select ICS File", options=[f["name"] for f in files]
)

# Find the selected file data
selected_file = next((f for f in files if f["name"] == selected_file_name), None)

if not selected_file:
    st.error("Select a file to continue")
    st.stop()

# --- Display File Details ---
st.subheader("File Details")
col1, col2 = st.columns(2)
col1.write(f"**Filename:** {selected_file['name']}")
col2.write(
    f"**Last Updated:** {selected_file['updated'].strftime('%Y-%m-%d %H:%M:%S')}"
)

# --- Display Metadata ---
st.json(selected_file["metadata"])

# --- Download Button ---
file_content = ics_storage.get_file_content(selected_file["name"])
st.sidebar.download_button(
    "Download ICS File",
    data=file_content,
    file_name=selected_file["name"],
    mime="text/calendar",
)

# --- Display Raw ICS Content ---
with st.expander("Raw ICS Content"):
    st.code(file_content, language="ics")

# --- Parse and Display Events ---
with st.expander("Parsed Events"):
    events = ics_parser.try_parse(file_content)
    if isinstance(events, IcsParsingError):
        st.error(f"Error parsing ICS file: {events}")
    else:
        event_data = [
            {
                "Start Time": event.start,
                "End Time": event.end,
                "Summary": event.title,
                "Description": event.description,
                "Location": event.location,
                # "UID": event.uid,
            }
            for event in events
        ]
    st.dataframe(event_data, use_container_width=True)
