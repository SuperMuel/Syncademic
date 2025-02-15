from datetime import datetime, timedelta

import streamlit as st
from firebase_admin import auth, storage

from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from functions.models.user import User
from functions.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
)
from functions.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
)
from functions.repositories.sync_stats_repository import (
    FirestoreSyncStatsRepository,
)
from functions.services.authorization_service import (
    AuthorizationService,
)
from functions.services.ics_service import (
    IcsService,
)
from functions.services.sync_profile_service import (
    SyncProfileService,
)
from functions.services.user_service import (
    FirebaseAuthUserService,
)
from functions.synchronizer.ics_cache import (
    FirebaseIcsFileStorage,
)

st.title("🔄 Sync Profiles")

# Initialize services
sync_profile_repo = FirestoreSyncProfileRepository()
user_service = FirebaseAuthUserService()

# Initialize authorization service
authorization_service = AuthorizationService(
    backend_auth_repo=FirestoreBackendAuthorizationRepository()
)

# Initialize sync profile service
sync_profile_service = SyncProfileService(
    sync_profile_repo=sync_profile_repo,
    authorization_service=authorization_service,
    sync_stats_repo=FirestoreSyncStatsRepository(),
    ics_service=IcsService(ics_storage=None),
)


@st.cache_data(ttl=60)
def get_all_users() -> dict[str, User]:
    """Get all users with their data."""
    users, _ = user_service.list_all_users()
    return {user.uid: user for user in users}


@st.cache_data(ttl=60)
def get_all_sync_profiles():
    """Get all sync profiles including invalid ones."""
    return sync_profile_repo.try_list_all_sync_profiles()


# Sidebar with refresh button and filters
with st.sidebar:
    st.header("Filters & Actions")

    refresh_button = st.button("🔄 Refresh Data", use_container_width=True)
    if refresh_button:
        get_all_users.clear()
        get_all_sync_profiles.clear()
        del st.session_state.sync_profile
        st.rerun()

    # Status filter
    status_filter = st.multiselect(
        "Filter by Status",
        options=[status.value for status in SyncProfileStatusType],
        default=[],
        help="Select one or more status types to filter profiles",
    )

    # Error filter
    error_filter = st.checkbox(
        "Show Only Profiles with Errors",
        help="Show only profiles that have errors or are invalid",
    )

# Fetch data
all_users = get_all_users()
all_profiles = get_all_sync_profiles()

# Apply filters
filtered_profiles = all_profiles

if status_filter:
    filtered_profiles = [
        p
        for p in filtered_profiles
        if isinstance(p, SyncProfile) and p.status.type.value in status_filter
    ]


if error_filter:
    filtered_profiles = [
        p
        for p in filtered_profiles
        if (not isinstance(p, SyncProfile))  # Invalid profiles
        or p.status.type == SyncProfileStatusType.FAILED  # Failed profiles
        or p.ruleset_error  # Profiles with ruleset errors
    ]

# Display stats
st.header("Statistics")
total_profiles = len(all_profiles)
valid_profiles = len([p for p in all_profiles if isinstance(p, SyncProfile)])
invalid_profiles = total_profiles - valid_profiles
failed_profiles = len(
    [
        p
        for p in all_profiles
        if isinstance(p, SyncProfile) and p.status.type == SyncProfileStatusType.FAILED
    ]
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Profiles", total_profiles)
col2.metric("Failed Profiles", failed_profiles)
col3.metric("Invalid Profiles", invalid_profiles)


if not filtered_profiles:
    st.info("No sync profiles match the current filters")
else:
    # Convert profiles to display format
    display_data = []
    for profile in filtered_profiles:
        if isinstance(profile, dict):
            # Handle invalid profile
            user = all_users.get(profile.get("user_id", ""), None)
            display_data.append(
                {
                    "Status": "❌ Invalid",
                    "User Email": user.email if user else "Unknown",
                    "User Name": user.display_name if user else "Unknown",
                    "Title": profile.get("title", "Invalid"),
                    "Created": "Unknown",
                    "Last Sync": "Never",
                    "Error": str(profile.get("ruleset_error", "Invalid profile data")),
                    "Calendar": profile.get("targetCalendar", {}).get("id", "Invalid"),
                    "Source": profile.get("scheduleSource", {}).get("url", "Invalid"),
                    # "_raw": profile,  # Store raw data for actions
                }
            )
        else:
            # Handle valid profile
            user = all_users.get(profile.user_id, None)
            display_data.append(
                {
                    "Status": profile.status.type.value,
                    "User Email": user.email if user else "Unknown",
                    "User Name": user.display_name if user else "Unknown",
                    "Title": profile.title,
                    "Created": profile.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if profile.created_at
                    else "Unknown",
                    "Last Sync": profile.lastSuccessfulSync.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if profile.lastSuccessfulSync
                    else "Never",
                    "Error": profile.ruleset_error or profile.status.message or "",
                    "Calendar": profile.targetCalendar.id,
                    "Source": str(profile.scheduleSource.url),
                    # "_raw": profile,  # Store raw data for actions
                }
            )

    # Display as dataframe with expandable rows
    selected = st.dataframe(
        display_data,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="Current status of the sync profile",
                width="small",
            ),
            "User Email": st.column_config.TextColumn(
                "User Email",
                help="Email of the profile owner",
                width="medium",
            ),
            "User Name": st.column_config.TextColumn(
                "User Name",
                help="Name of the profile owner",
                width="medium",
            ),
            "Title": st.column_config.TextColumn(
                "Title",
                help="Profile title",
                width="medium",
            ),
            "Created": st.column_config.TextColumn(
                "Created",
                help="When the profile was created",
                width="medium",
            ),
            "Last Sync": st.column_config.TextColumn(
                "Last Sync",
                help="Last successful synchronization",
                width="medium",
            ),
            "Error": st.column_config.TextColumn(
                "Error",
                help="Error message if any",
                width="large",
            ),
            "Calendar": st.column_config.TextColumn(
                "Calendar ID",
                help="Target Google Calendar ID",
                width="medium",
            ),
            "Source": st.column_config.LinkColumn(
                "Source URL",
                help="Source schedule URL",
                width="large",
            ),
            "_raw": st.column_config.Column(
                "Raw Data",
                help="Raw profile data",
            ),
        },
        hide_index=True,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
    )

    if selected["selection"]["rows"]:
        profile = filtered_profiles[selected["selection"]["rows"][0]]
        st.session_state.sync_profile = profile  # TODO : instead of the full object, store the id. That way, we can always get updated data, or re-select by id when data change


# Display selected profile details
if st.session_state.get("sync_profile"):
    st.header("Selected Profile Details")
    profile = st.session_state.sync_profile

    if isinstance(profile, dict):
        st.error("Invalid Profile Data")
        st.json(profile)

        # Add delete button for invalid profiles
        if st.button("🗑️ Delete Invalid Profile", type="primary"):
            try:
                sync_profile_repo.delete_sync_profile(
                    profile.get("user_id", ""), profile.get("id", "")
                )
                st.success("Profile deleted successfully!")
                # Clear cache and rerun
                get_all_sync_profiles.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete profile: {str(e)}")

    else:
        # Show profile details
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Profile Info")
            st.write(f"**ID:** {profile.id}")
            st.write(f"**User ID:** {profile.user_id}")
            st.write(f"**Title:** {profile.title}")
            st.write(f"**Status:** {profile.status.type.value}")
            if profile.status.message:
                st.write(f"**Status Message:** {profile.status.message}")

            st.write(
                f"**Created:** {profile.created_at.strftime('%Y-%m-%d %H:%M:%S') if profile.created_at else 'Unknown'}"
            )
            st.write(
                f"**Last Sync:** {profile.lastSuccessfulSync.strftime('%Y-%m-%d %H:%M:%S') if profile.lastSuccessfulSync else 'Never'}"
            )

        with col2:
            st.subheader("Calendar Info")
            st.write(f"**Calendar ID:** {profile.targetCalendar.id}")
            st.write(
                f"**Calendar Email:** {profile.targetCalendar.providerAccountEmail}"
            )
            st.write(f"**Source URL:** {profile.scheduleSource.url}")

        # Show ruleset if exists
        if profile.ruleset:
            with st.expander("View Ruleset"):
                st.json(profile.ruleset.model_dump())

        # Add action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Retry Sync", use_container_width=True):
                try:
                    sync_profile_service.synchronize(
                        user_id=profile.user_id,
                        sync_profile_id=profile.id,
                        sync_trigger=SyncTrigger.MANUAL,
                        sync_type=SyncType.REGULAR,
                    )
                    st.success("Sync triggered successfully!")
                except Exception as e:
                    st.error(f"Failed to trigger sync: {str(e)}")

        with col2:
            if st.button("🔍 Check Calendar", use_container_width=True):
                try:
                    calendar_manager = authorization_service.get_authenticated_google_calendar_manager(
                        user_id=profile.user_id,
                        provider_account_id=profile.targetCalendar.providerAccountId,
                        calendar_id=profile.targetCalendar.id,
                    )
                    if calendar_manager.check_calendar_exists():
                        st.success("✅ Calendar exists and is accessible")
                    else:
                        st.error("❌ Calendar does not exist or is not accessible")
                except Exception as e:
                    st.error(f"Failed to check calendar: {str(e)}")

        with col3:
            if st.button("🗑️ Delete Profile", type="primary", use_container_width=True):
                try:
                    sync_profile_repo.delete_sync_profile(profile.user_id, profile.id)
                    st.success("Profile deleted successfully!")
                    # Clear cache and rerun
                    get_all_sync_profiles.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete profile: {str(e)}")
