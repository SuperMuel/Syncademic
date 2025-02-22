from datetime import datetime
import streamlit as st

from admin.shared.data_service import data_service

st.title("🧑‍🤝‍🧑 Users")

# --- Sidebar Filters ---
with st.sidebar:
    refresh_button = st.button("🔄 Refresh User List", use_container_width=True)

    if refresh_button:
        del st.session_state.user
        data_service.clear_all_caches()
        st.rerun()

# --- Fetch and Filter Users ---
all_users = list(data_service.get_all_users().values())

# Sort users by signup date
all_users.sort(
    key=lambda x: x.user_metadata.creation_timestamp or datetime.min, reverse=True
)

# --- Display Users ---
user_data = [
    {
        "uid": user.uid,
        "email": user.email,
        "display_name": user.display_name,
        "signup_date": user.user_metadata.creation_timestamp,
        "last_sign_in_date": user.user_metadata.last_sign_in_timestamp,
        "disabled": user.disabled,
    }
    for user in all_users
]

st.info("Select a user from the table below to view their details", icon="👇")

selected = st.dataframe(
    user_data,
    column_config={
        "signup_date": st.column_config.DateColumn("Signup Date", format="YYYY-MM-DD"),
        "last_sign_in_date": st.column_config.DateColumn(
            "Last Sign-in Date", format="YYYY-MM-DD"
        ),
        "disabled": st.column_config.CheckboxColumn(
            "Disabled", help="Is user account disabled?"
        ),
    },
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row",
)

if selected["selection"]["rows"]:  # type: ignore
    st.header("Selected User")
    user = user_data[selected["selection"]["rows"][0]]  # type: ignore
    st.session_state.user = user
    st.write(st.session_state.user)
