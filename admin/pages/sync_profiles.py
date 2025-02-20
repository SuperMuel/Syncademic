import streamlit as st

from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from functions.models.rules import Ruleset
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
def get_all_sync_profiles() -> list[SyncProfile]:
    """Get all valid sync profiles."""
    return sync_profile_repo.list_all_sync_profiles()


def _clear_cache_and_rerun():
    get_all_users.clear()
    get_all_sync_profiles.clear()
    st.rerun()


def _get_selected_profile() -> SyncProfile | None:
    user_id_profile_id = st.session_state.get("user_id_profile_id")

    if not user_id_profile_id:
        return None

    assert (
        isinstance(user_id_profile_id, tuple)
        and len(user_id_profile_id) == 2
        and isinstance(user_id_profile_id[0], str)
        and isinstance(user_id_profile_id[1], str)
    )

    if not user_id_profile_id:
        return None

    user_id, profile_id = user_id_profile_id

    result = sync_profile_repo.get_sync_profile(user_id, profile_id)
    if result is None:
        st.error(f"Selected sync profile with id {profile_id} not found", icon="❌")
        return None

    return result


# Sidebar with refresh button and filters
with st.sidebar:
    st.header("Filters & Actions")

    refresh_button = st.button("🔄 Refresh Data", use_container_width=True)
    if refresh_button:
        _clear_cache_and_rerun()

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
        help="Show only profiles that have errors (Satus failed), or Ruleset geneartion error.",
    )

# Fetch data
all_users = get_all_users()
all_profiles = get_all_sync_profiles()

all_profiles.sort(key=lambda x: x.created_at, reverse=True)

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
failed_profiles = len(
    [p for p in all_profiles if p.status.type == SyncProfileStatusType.FAILED]
)

col1, col2 = st.columns(2)
col1.metric("Total Profiles", total_profiles)
col2.metric("Failed Profiles", failed_profiles)


if not filtered_profiles:
    st.info("No sync profiles match the current filters")
    st.stop()

if not st.session_state.get("user_id_profile_id"):
    st.info("Select a profile to view details", icon="ℹ️")

# Convert profiles to display format
display_data = []
for profile in filtered_profiles:
    user = all_users.get(profile.user_id, None)
    display_data.append(
        {
            "Status": profile.status.type.value,
            "User Email": user.email if user else None,
            "User Name": user.display_name if user else None,
            "Title": profile.title,
            "Created": profile.created_at,
            "Last Sync": profile.lastSuccessfulSync,
            "Error": profile.status.message,
            "Calendar": profile.targetCalendar.id,
            "Source": str(profile.scheduleSource.url),
            "Ruleset Error": profile.ruleset_error,
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
        "Created": st.column_config.DatetimeColumn(
            "Created",
            help="When the profile was created",
            width="medium",
        ),
        "Last Sync": st.column_config.DatetimeColumn(
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
    },
    hide_index=True,
    use_container_width=True,
    selection_mode="single-row",
    on_select="rerun",
)

if selected["selection"]["rows"]:  # type: ignore
    profile = filtered_profiles[selected["selection"]["rows"][0]]  # type: ignore
    st.session_state.user_id_profile_id = (profile.user_id, profile.id)


def _check_calendar(user_id: str, profile: SyncProfile) -> None:
    """
    Verify authorization and check the existence of the target Google Calendar for a sync profile.

    This function first tests whether the specified user is authorized to access the Google Calendar
    associated with the provided sync profile. If the authorization passes, it retrieves an authenticated
    Google Calendar manager and checks if the target calendar exists.

    Args:
        user_id (str): The identifier of the user who owns the sync profile.
        profile (SyncProfile): The synchronization profile containing calendar and authorization details.

    Returns:
        None
    """
    with st.spinner("Checking authorization..."):
        try:
            authorization_service.test_authorization(
                user_id=profile.user_id,
                provider_account_id=profile.targetCalendar.providerAccountId,
            )
            st.success("Authorization valid", icon="✅")
        except Exception as e:
            st.error(f"Failed to check authorization: {str(e)}", icon="❌")
            return

    calendar_manager = authorization_service.get_authenticated_google_calendar_manager(
        user_id=profile.user_id,
        provider_account_id=profile.targetCalendar.providerAccountId,
        calendar_id=profile.targetCalendar.id,
    )

    if calendar_manager.check_calendar_exists():
        st.success("Calendar exists and is accessible", icon="✅")
    else:
        st.error("Calendar does not exist", icon="❌")


@st.dialog(title="Delete Profile")
def delete_sync_profile_dialog(profile: SyncProfile) -> None:
    if st.button("Confirm Delete", use_container_width=True):
        try:
            with st.spinner("Deleting profile..."):
                sync_profile_repo.delete_sync_profile(profile.user_id, profile.id)
                st.success("Profile deleted successfully!", icon="✅")
                _clear_cache_and_rerun()
        except Exception as e:
            st.error("Failed to delete profile:", icon="❌")
            st.exception(e)


@st.dialog(title="Edit Ruleset")
def edit_ruleset_dialog(profile: SyncProfile) -> None:
    """Dialog to edit a sync profile's ruleset."""
    st.header(f"`{profile.title}`")
    st.write(
        "Paste a valid ruleset JSON below. The ruleset must contain at least one rule with a condition and actions."
    )

    # Default to current ruleset if it exists
    default_json = profile.ruleset.model_dump_json() if profile.ruleset else "{}"
    ruleset_json = st.text_area("Ruleset JSON", value=default_json, height=300)

    if st.button("Update Ruleset", use_container_width=True):
        try:
            # Validate the JSON string can be parsed into a Ruleset
            new_ruleset = Ruleset.model_validate_json(ruleset_json)

            # Update the ruleset in the database
            sync_profile_repo.update_ruleset(profile.user_id, profile.id, new_ruleset)

            # Clear any previous ruleset error
            sync_profile_repo.update_ruleset_error(profile.user_id, profile.id, None)

            st.success("Ruleset updated successfully!", icon="✅")
            _clear_cache_and_rerun()

        except Exception as e:
            st.error("Failed to update ruleset", icon="❌")
            st.exception(e)


# Display selected profile details
if profile := _get_selected_profile():
    st.header("Selected Profile Details")

    # Show profile details
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Profile Info")
        st.write(f"**ID:** {profile.id}")
        st.write(f"**User ID:** {profile.user_id}")
        st.write(f"**Title:** {profile.title}")
        st.write(f"**Status:** {profile.status.type.value}")
        if profile.status.message:
            st.write("**Status Error:**")
            st.error(profile.status.message)

        st.write(
            f"**Created:** {profile.created_at.strftime('%Y-%m-%d %H:%M:%S') if profile.created_at else 'Unknown'}"
        )
        st.write(
            f"**Last Sync:** {profile.lastSuccessfulSync.strftime('%Y-%m-%d %H:%M:%S') if profile.lastSuccessfulSync else 'Never'}"
        )

    with col2:
        st.subheader("Calendar Info")
        st.write(f"**Calendar ID:** {profile.targetCalendar.id}")
        st.write(f"**Calendar Email:** {profile.targetCalendar.providerAccountEmail}")
        st.write(f"**Source URL:** {profile.scheduleSource.url}")

    if profile.ruleset_error:
        st.error(profile.ruleset_error)

    # Add action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Retry Sync", use_container_width=True):
            with st.spinner("Retrying sync..."):
                try:
                    sync_profile_service.synchronize(
                        user_id=profile.user_id,
                        sync_profile_id=profile.id,
                        sync_trigger=SyncTrigger.MANUAL,
                        sync_type=SyncType.REGULAR,
                        force=True,
                    )
                    st.success("Sync triggered successfully!")
                except Exception as e:
                    st.error(f"Failed to trigger sync: {str(e)}")

            _clear_cache_and_rerun()
    with col2:
        if st.button("🔍 Check Calendar", use_container_width=True):
            _check_calendar(profile.user_id, profile)

    with col3:
        if st.button("🗑️ Delete Profile", type="primary", use_container_width=True):
            delete_sync_profile_dialog(profile)

    # Add ruleset editing section
    st.subheader("Ruleset")
    if profile.ruleset:
        with st.expander("Current Ruleset"):
            st.json(profile.ruleset.model_dump())

    if st.button("✏️ Edit Ruleset", use_container_width=True):
        edit_ruleset_dialog(profile)
