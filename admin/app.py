import streamlit as st
from dotenv import load_dotenv
from firebase_admin import auth, initialize_app, storage
from pydantic import ValidationError

from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
)
from functions.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
)
from functions.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
)
from functions.repositories.sync_stats_repository import FirestoreSyncStatsRepository
from functions.services.authorization_service import AuthorizationService
from functions.services.ics_service import IcsService
from functions.services.sync_profile_service import SyncProfileService
from functions.synchronizer.ics_cache import FirebaseIcsFileStorage

load_dotenv()

st.set_page_config(
    page_title="Syncademic Admin Panel",
    layout="wide",
)


@st.cache_resource()
def init_firebase():
    initialize_app()


init_firebase()

st.title("Syncademic Admin Panel")

# Initialize repository
repo = FirestoreSyncProfileRepository()
authorization_service = AuthorizationService(
    backend_auth_repo=FirestoreBackendAuthorizationRepository()
)
sync_profile_service = SyncProfileService(
    sync_profile_repo=repo,
    sync_stats_repo=FirestoreSyncStatsRepository(),
    authorization_service=authorization_service,
    ics_service=IcsService(
        ics_storage=FirebaseIcsFileStorage(bucket=storage.bucket("default"))
    ),
)


@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_profiles():
    return repo.try_list_all_sync_profiles()


# Fetch all profiles
profiles = fetch_profiles()


@st.cache_data(ttl=60)
def list_all_users(max_results=1000, page_token=None):
    """
    Lists all Firebase users in your project, handling pagination.

    Args:
        max_results: The maximum number of users to return per page (max 1000).
        page_token: The next page token from a previous call (for pagination).

    Returns:
        A list of UserRecord objects and the next page token (if available).
    """
    page = auth.list_users(max_results=max_results, page_token=page_token)
    users = []

    for user in page.users:
        user_data = {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "phone_number": user.phone_number,
            "disabled": user.disabled,
            "email_verified": user.email_verified,
            "provider_data": [
                {
                    "provider_id": provider.provider_id,
                    "uid": provider.uid,
                    "email": provider.email,
                    "display_name": provider.display_name,
                    "photo_url": provider.photo_url,
                    "phone_number": provider.phone_number,
                }
                for provider in user.provider_data
            ],  # Information about the providers used to sign in (e.g., Google, Facebook)
            "custom_claims": user.custom_claims,
            "password_hash": user.password_hash,
            "password_salt": user.password_salt,
            "tokens_valid_after_time": user.tokens_valid_after_timestamp,
            "user_metadata": {
                "creation_timestamp": user.user_metadata.creation_timestamp,
                "last_sign_in_timestamp": user.user_metadata.last_sign_in_timestamp,
            },
        }
        users.append(user_data)

    # If there's another page, recursively call list_all_users
    if page.has_next_page:
        next_page_users, _ = list_all_users(
            max_results=max_results, page_token=page.next_page_token
        )
        users.extend(next_page_users)

    return users, page.next_page_token


all_users, _ = list_all_users()
all_users_dict = {user["uid"]: user for user in all_users}


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
                    "User Email": next(
                        (u["email"] for u in all_users if u["uid"] == p.get("user_id")),
                        "Unknown",
                    ),
                    "User Name": next(
                        (
                            u["display_name"]
                            for u in all_users
                            if u["uid"] == p.get("user_id")
                        ),
                        "Unknown",
                    ),
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
                    "User Email": next(
                        (u["email"] for u in all_users if u["uid"] == p.user_id),
                        "Unknown",
                    ),
                    "User Name": next(
                        (u["display_name"] for u in all_users if u["uid"] == p.user_id),
                        "Unknown",
                    ),
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
                    "Ruleset Error": p.ruleset_error,
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
            "User Email": st.column_config.TextColumn("User Email", width="medium"),
            "User Name": st.column_config.TextColumn("User Name", width="medium"),
            "Profile ID": st.column_config.TextColumn("Profile ID", width="medium"),
            "Title": st.column_config.TextColumn("Title", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Status Message": st.column_config.TextColumn(
                "Status Message", width="large"
            ),
            "Last Sync": st.column_config.TextColumn("Last Sync", width="medium"),
            "Created": st.column_config.TextColumn("Created", width="medium"),
            "Ruleset Error": st.column_config.TextColumn(
                "Ruleset Error", width="large"
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
        with st.expander(
            f"{all_users_dict.get(profile.user_id, {}).get('email', 'Unknown User')} - {profile.title} - Error: {profile.status.message}"
        ):
            st.write("Profile Details:")
            st.json(profile.model_dump())

            retry_col, check_cal_col, delete_col = st.columns([1, 1, 1])

            # Add retry button
            if retry_col.button(
                "🔄 Retry Sync",
                key=f"retry_{profile.id}",
                type="secondary",
                use_container_width=True,
            ):
                st.toast(f"Triggered sync retry for profile {profile.id}")
                sync_profile_service.synchronize(
                    user_id=profile.user_id,
                    sync_profile_id=profile.id,
                    sync_trigger=SyncTrigger.MANUAL,
                    sync_type=SyncType.REGULAR,
                )
                st.cache_data.clear()
                st.rerun()

            # Add check calendar button
            if check_cal_col.button(
                "🔍 Check Calendar",
                key=f"check_cal_{profile.id}",
                type="secondary",
                use_container_width=True,
            ):
                try:
                    calendar_manager = authorization_service.get_authenticated_google_calendar_manager(
                        user_id=profile.user_id,
                        provider_account_id=profile.targetCalendar.providerAccountId,
                        calendar_id=profile.targetCalendar.id,
                    )
                    if calendar_manager.check_calendar_exists():
                        st.toast("✅ Calendar exists and is accessible")
                    else:
                        st.toast(
                            "❌ Calendar does not exist or is not accessible", icon="⚠️"
                        )
                except Exception as e:
                    st.toast(f"❌ Error checking calendar: {str(e)}", icon="⚠️")

            # Add delete button with confirmation
            if delete_col.button(
                "🗑️ Delete Profile",
                key=f"delete_failed_{profile.id}",
                type="secondary",
                use_container_width=True,
            ):
                if delete_col.button(
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


st.header(f"Users ({len(all_users)})")

# Create dataframe with image column
df = st.dataframe(
    all_users,
    column_config={
        "photo_url": st.column_config.ImageColumn(
            "Photo",
            width="small",
            help="User profile photo",
        )
    },
    hide_index=True,
    use_container_width=True,
)
