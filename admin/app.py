import streamlit as st
from functions.models.sync_profile import SyncProfile
from functions.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
)

st.set_page_config(
    page_title="Syncademic Admin Panel",
    layout="wide",
)

st.title("Syncademic Admin Panel")

# Initialize repository
repo = FirestoreSyncProfileRepository()


@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_profiles():
    return repo.try_list_all_sync_profiles()


# Fetch all profiles
profiles = fetch_profiles()


def display_sync_profiles(profiles: list[SyncProfile | dict]) -> None:
    # Display profiles in a table
    if not profiles:
        st.info("No sync profiles found")
        return

    # Convert profiles to a list of dictionaries for display
    profile_data = []
    for p in profiles:
        if isinstance(p, dict):
            # Handle raw dict case for invalid profiles
            profile_data.append(
                {
                    "User ID": p.get("user_id", "Invalid"),
                    "Profile ID": p.get("id", "Invalid"),
                    "Title": p.get("title", "Invalid"),
                    "Status": "Invalid Profile",
                    "Status Message": "Invalid Profile Data",
                    "Last Sync": "Unknown",
                    "Created": "Unknown",
                    "Has Error": "Yes",
                    "Error Message": str(
                        p.get("ruleset_error", "Invalid profile data")
                    ),
                    "Calendar ID": p.get("targetCalendar", {}).get("id", "Invalid"),
                    "Calendar Email": p.get("targetCalendar", {}).get(
                        "providerAccountEmail", "Invalid"
                    ),
                    "Source URL": p.get("scheduleSource", {}).get("url", "Invalid"),
                }
            )
        else:
            # Handle valid SyncProfile case
            profile_data.append(
                {
                    "User ID": p.user_id,
                    "Profile ID": p.id,
                    "Title": p.title,
                    "Status": p.status.type.value,
                    "Status Message": p.status.message or "No message",
                    "Last Sync": p.lastSuccessfulSync.strftime("%Y-%m-%d %H:%M:%S")
                    if p.lastSuccessfulSync
                    else "Never",
                    "Created": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if p.created_at
                    else "Unknown",
                    "Has Error": "Yes" if p.ruleset_error else "No",
                    "Error Message": p.ruleset_error or "No error",
                    "Calendar ID": p.targetCalendar.id,
                    "Calendar Email": p.targetCalendar.providerAccountEmail,
                    "Source URL": str(p.scheduleSource.url),
                }
            )

    st.dataframe(
        profile_data,
        use_container_width=True,
        column_config={
            "User ID": st.column_config.TextColumn("User ID", width="medium"),
            "Profile ID": st.column_config.TextColumn("Profile ID", width="medium"),
            "Title": st.column_config.TextColumn("Title", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Status Message": st.column_config.TextColumn(
                "Status Message", width="large"
            ),
            "Last Sync": st.column_config.TextColumn("Last Sync", width="medium"),
            "Created": st.column_config.TextColumn("Created", width="medium"),
            "Has Error": st.column_config.TextColumn("Has Error", width="small"),
            "Error Message": st.column_config.TextColumn(
                "Error Message", width="large"
            ),
            "Calendar ID": st.column_config.TextColumn("Calendar ID", width="medium"),
            "Calendar Email": st.column_config.TextColumn(
                "Calendar Email", width="medium"
            ),
            "Source URL": st.column_config.LinkColumn("Source URL", width="large"),
        },
    )


display_sync_profiles(profiles)
