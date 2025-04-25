from functions.ai.ruleset_builder import RulesetBuilder
from functions.infrastructure.event_bus import MockEventBus
import streamlit as st

from functions.models.sync_profile import (
    ScheduleSource,
    SyncProfile,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from functions.models.rules import Ruleset
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
from functions.services.ai_ruleset_service import (
    AiRulesetService,
)
from admin.shared.event_display import (
    apply_rules,
    display_events_calendar,
    display_events_dataframe,
)
from admin.shared.data_service import data_service

st.title("🔄 Sync Profiles")

# Initialize services

event_bus = MockEventBus()

sync_profile_repo = FirestoreSyncProfileRepository()

# Initialize authorization service
authorization_service = AuthorizationService(
    backend_auth_repo=FirestoreBackendAuthorizationRepository()
)

# Initialize sync profile service
sync_profile_service = SyncProfileService(
    sync_profile_repo=sync_profile_repo,
    authorization_service=authorization_service,
    sync_stats_repo=FirestoreSyncStatsRepository(),
    ics_service=IcsService(event_bus=event_bus),
)

# Initialize AI ruleset service
ai_ruleset_service = AiRulesetService(
    ics_service=IcsService(event_bus=event_bus),
    sync_profile_repo=sync_profile_repo,
    ruleset_builder=RulesetBuilder(),
)


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
        data_service.clear_all_caches()
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
        help="Show only profiles that have errors (Satus failed), or Ruleset geneartion error.",
    )

# Fetch data
all_users = data_service.get_all_users()
all_profiles = data_service.get_all_sync_profiles()

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
sync_profile_stats = data_service.get_sync_profile_stats()

col1, col2, col3 = st.columns(3)
col1.metric("🔄 Total Profiles", sync_profile_stats["total"])
col2.metric("🏃 In Progress", sync_profile_stats["in_progress"])
col3.metric("❌ Failed", sync_profile_stats["failed"])


if not filtered_profiles:
    st.info("No sync profiles match the current filters")
    st.stop()

if not st.session_state.get("user_id_profile_id"):
    st.info("Select a profile to view details", icon="ℹ️")


def _status_to_label(status: SyncProfileStatusType) -> str:
    match status:
        case SyncProfileStatusType.FAILED:
            return "❌ Failed"
        case SyncProfileStatusType.IN_PROGRESS:
            return "🏃 In Progress"
        case SyncProfileStatusType.SUCCESS:
            return "✅ Success"
        case SyncProfileStatusType.DELETING:
            return "🗑️ Deleting"
        case SyncProfileStatusType.DELETION_FAILED:
            return "❌ Deletion Failed"
        case SyncProfileStatusType.NOT_STARTED:
            return "⏳ Not Started"

    raise ValueError(f"Unknown status: {status}")


# Convert profiles to display format
display_data = []
for profile in filtered_profiles:
    user = all_users.get(profile.user_id, None)
    display_data.append(
        {
            "Status": _status_to_label(profile.status.type),
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
        "Ruleset Error": st.column_config.TextColumn(
            "Ruleset Error",
            help="Error message if any",
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
                data_service.clear_all_caches()
                st.rerun()
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
    default_json = (
        profile.ruleset.model_dump_json(indent=4) if profile.ruleset else "{}"
    )
    ruleset_json = st.text_area("Ruleset JSON", value=default_json, height=300)

    if st.button("Update Ruleset", use_container_width=True):
        try:
            # Validate the JSON string can be parsed into a Ruleset
            new_ruleset = Ruleset.model_validate_json(ruleset_json)

            # Update the ruleset in the database
            profile.update_ruleset(ruleset=new_ruleset)
            sync_profile_repo.save_sync_profile(profile)

            st.success("Ruleset updated successfully!", icon="✅")
            data_service.clear_all_caches()
            st.rerun()

        except Exception as e:
            st.error("Failed to update ruleset", icon="❌")
            st.exception(e)


@st.cache_data(
    ttl=60,
    show_spinner="Fetching events...",
    hash_funcs={ScheduleSource: lambda x: x.model_dump_json()},
)
def fetch_events(
    source: ScheduleSource,
):
    """
    Fetches and parses calendar events from the given schedule source.
    
    Args:
        source: The schedule source from which to retrieve events.
    
    Returns:
        A list of parsed events if successful, or an error message string if fetching or parsing fails.
    """
    return IcsService(event_bus=event_bus).try_fetch_and_parse(
        ics_source=source.to_ics_source(),
        metadata={"source": source.model_dump()},
    )


@st.dialog(title="Retry Sync")
def retry_sync_dialog(profile: SyncProfile) -> None:
    """Dialog to select sync type and trigger a sync."""
    st.write("Choose the type of synchronization to perform:")

    def _format_sync_type(x: SyncType) -> str:
        match x:
            case SyncType.REGULAR:
                return "Regular (only future events)"
            case SyncType.FULL:
                return "Full (all events)"

    sync_type = st.segmented_control(
        "Sync Type",
        options=[SyncType.REGULAR, SyncType.FULL],
        default=SyncType.REGULAR,
        format_func=_format_sync_type,
        help="Regular sync only updates future events, while full sync refreshes all events.",
    )

    if not sync_type:
        st.error("Please select a sync type", icon="❌")
    elif st.button("Start Sync", use_container_width=True, type="primary"):
        with st.spinner("Syncing..."):
            try:
                sync_profile_service.synchronize(
                    user_id=profile.user_id,
                    sync_profile_id=profile.id,
                    sync_trigger=SyncTrigger.MANUAL,
                    sync_type=sync_type,
                    force=True,
                )
                st.success("Sync triggered successfully!")
            except Exception as e:
                st.error(f"Failed to trigger sync: {str(e)}")

        data_service.clear_all_caches()
        st.rerun()


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
    col1, col2, col3, col4 = st.columns(4)  # Add a column for the new button

    with col1:
        if st.button("🔄 Retry Sync", use_container_width=True):
            retry_sync_dialog(profile)

    with col2:
        if st.button("🔍 Check Calendar", use_container_width=True):
            _check_calendar(profile.user_id, profile)

    with col3:
        if st.button("🗑️ Delete Profile", type="primary", use_container_width=True):
            delete_sync_profile_dialog(profile)

    with col4:  # New button for regenerating ruleset
        if st.button("✨ Regenerate Ruleset", use_container_width=True):
            with st.spinner("Regenerating ruleset..."):
                try:
                    ai_ruleset_service.create_ruleset_for_sync_profile(profile)
                except Exception as e:
                    st.error(f"Failed to regenerate ruleset: {str(e)}", icon="❌")
            data_service.clear_all_caches()
            st.rerun()

    # Add ruleset editing section
    st.subheader("Ruleset")
    if profile.ruleset:
        with st.expander("Current Ruleset"):
            st.json(profile.ruleset.model_dump())

    if st.button("✏️ Edit Ruleset", use_container_width=True):
        edit_ruleset_dialog(profile)

    # Add events section
    st.subheader("Events")

    # Fetch events
    print("fetching events")
    events_or_error = fetch_events(profile.scheduleSource)
    if isinstance(events_or_error, Exception):
        st.error(f"Failed to fetch events: {str(events_or_error)}")
    else:
        before_events = events_or_error.events

        if should_apply_rules := st.checkbox(
            "Apply Rules",
            value=profile.ruleset is not None,
        ):
            after_events = apply_rules(before_events, profile.ruleset)
        else:
            after_events = before_events

        print("displaying calendar")
        calendar_value = display_events_calendar(
            after_events, key=f"calendar_view_{profile.id}_{str(should_apply_rules)}"
        )

        st.divider()

        # If you want to see what the user does (click events, etc.):
        st.write(calendar_value)
        # Show events before rules
        st.subheader("Original Events")
        display_events_dataframe(before_events)

        # Show events after rules if ruleset exists
        if profile.ruleset:
            st.subheader("Events After Rules")
            display_events_dataframe(after_events)
