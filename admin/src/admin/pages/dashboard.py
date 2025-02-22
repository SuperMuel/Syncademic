import streamlit as st

from admin.shared.data_service import data_service

st.title("🏠 Dashboard")

# Sidebar with refresh button
with st.sidebar:
    refresh_button = st.button("🔄 Refresh Cached Data", use_container_width=True)
    if refresh_button:
        data_service.clear_all_caches()
        st.rerun()

# --- Fetch Data ---
total_users = len(data_service.get_all_users())
recent_signups = data_service.get_recent_signups()
sync_profile_stats = data_service.get_sync_profile_stats()

# --- Display Metrics ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("👤 Total Users", total_users)
col2.metric("🔄 Total Sync Profiles", sync_profile_stats["total"])
col3.metric("🏃 In Progress", sync_profile_stats["in_progress"])
col4.metric("❌ Failed", sync_profile_stats["failed"])

# --- Recent Sign-ups ---
st.header("👤 Recent User Sign-ups")

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
