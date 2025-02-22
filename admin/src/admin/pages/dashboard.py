import streamlit as st
from admin.shared.event_display import display_events

from functions.models.user import User
from functions.services.user_service import FirebaseAuthUserService

st.title("🏠 Dashboard")

# Initialize services
user_service = FirebaseAuthUserService()


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_total_users() -> int:
    """Get the total number of users."""
    print("Getting total users")
    users, _ = user_service.list_all_users()
    return len(users)


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_recent_signups(n: int = 10) -> list[User]:
    """Get the n most recent user signups."""
    print("Getting recent signups")
    return user_service.get_recent_signups(limit=n)


# Sidebar with refresh button
with st.sidebar:
    refresh_button = st.button("🔄 Refresh Cached Data", use_container_width=True)

    if refresh_button:
        print("Refreshing")
        get_total_users.clear()
        get_recent_signups.clear()


# --- Fetch Data ---
total_users = get_total_users()
recent_signups = get_recent_signups()

# --- Display Metrics ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", total_users)
# col2.metric("Total Sync Profiles", 523)  # TODO: Implement sync profile metrics
# col3.metric("Sync Profiles - In Progress", 25)  # TODO: Implement sync profile metrics
# col4.metric(
#     "Sync Profiles - Failed",
#     12,  # TODO: Implement sync profile metrics
#     delta=-12,
#     delta_color="inverse",
# )


# --- Recent Sign-ups ---
st.header("Recent User Sign-ups")

# Convert recent signups to a format suitable for the dataframe
recent_signup_data = [
    {
        "email": user.email,
        "display_name": user.display_name,
        "signup_date": user.user_metadata.creation_timestamp,
    }
    for user in recent_signups
]

st.dataframe(
    recent_signup_data,
    column_config={
        "signup_date": st.column_config.DateColumn("Signup Date", format="YYYY-MM-DD")
    },
    hide_index=True,
    use_container_width=True,
)
