import streamlit as st
from pydantic import ValidationError

from functions.models.sync_profile import SyncProfile, SyncProfileStatusType
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

# Display invalid profiles section
invalid_profiles = [p for p in profiles if isinstance(p, dict)]

if invalid_profiles:
    st.header("Invalid Sync Profiles")
    st.write("The following sync profiles failed validation:")

    for profile in invalid_profiles:
        with st.expander(
            f"Invalid Profile - User: {profile.get('user_id', 'Unknown')}, ID: {profile.get('id', 'Unknown')}"
        ):
            try:
                # Try to validate again to get the specific error
                SyncProfile.model_validate(profile)
            except ValidationError as e:
                st.code(str(e), language="text")

            st.write("Raw Profile Data:")
            st.json(profile)

            # Add delete button
            if st.button(
                "Delete Profile",
                key=f"delete_{profile.get('id')}",
                type="primary",
                use_container_width=True,
            ):
                user_id = profile.get("user_id")
                profile_id = profile.get("id")
                if not user_id or not profile_id:
                    st.error("Missing user_id or profile_id")
                    print(f"Missing user_id or profile_id: {user_id=} {profile_id=}")
                    continue
                repo.delete_sync_profile(user_id, profile_id)
                st.toast(f"Profile {profile_id} deleted successfully!")
                print(f"Deleted profile {profile_id} for user {user_id}")
                st.cache_data.clear()
                st.rerun()

# Display failed profiles section
failed_profiles = [
    p
    for p in profiles
    if isinstance(p, SyncProfile) and p.status.type == SyncProfileStatusType.FAILED
]

if failed_profiles:
    st.header("Failed Sync Profiles")
    st.write("The following sync profiles are in a failed state:")

    for profile in failed_profiles:
        with st.expander(f"Failed Profile - User: {profile.user_id}, ID: {profile.id}"):
            st.write("Profile Details:")
            st.json(profile.model_dump())

            # Add retry button
            if st.button(
                "Retry Sync",
                key=f"retry_{profile.id}",
                type="primary",
                use_container_width=True,
            ):
                st.toast(f"Triggered sync retry for profile {profile.id}")
                # Note: You'll need to implement the retry functionality
                st.cache_data.clear()
                st.rerun()

            # Add delete button with confirmation
            if st.button(
                "Delete Profile",
                key=f"delete_failed_{profile.id}",
                type="secondary",
                use_container_width=True,
            ):
                if st.button(
                    "Click again to confirm deletion",
                    key=f"confirm_delete_failed_{profile.id}",
                    type="primary",
                    use_container_width=True,
                ):
                    repo.delete_sync_profile(profile.user_id, profile.id)
                    st.toast(f"Profile {profile.id} deleted successfully!")
                    print(
                        f"Deleted failed profile {profile.id} for user {profile.user_id}"
                    )
                    st.cache_data.clear()
                    st.rerun()
