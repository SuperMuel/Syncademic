from datetime import datetime

import streamlit as st

from backend.models.authorization import BackendAuthorization
from backend.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
)
from backend.services.authorization_service import AuthorizationService
from admin.shared.data_service import data_service

st.title("🔑 Backend Authorizations")

# Initialize services and repositories
authorization_service = AuthorizationService(
    backend_auth_repo=FirestoreBackendAuthorizationRepository()
)
backend_auth_repo = FirestoreBackendAuthorizationRepository()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filters & Actions")

    refresh_button = st.button("🔄 Refresh Data", use_container_width=True)
    if refresh_button:
        data_service.clear_all_caches()
        st.rerun()

# --- Fetch and Filter Authorizations ---
all_users = data_service.get_all_users()
all_authorizations = data_service.get_all_authorizations()

# Apply filters
filtered_authorizations = all_authorizations

# --- Display Authorizations ---
st.header("Backend Authorizations")

if not filtered_authorizations:
    st.info("No authorizations found")
    st.stop()

authorization_data = [
    {
        "User ID": auth.userId,
        "User Email": all_users[auth.userId].email
        if auth.userId in all_users
        else None,
        "Provider": auth.provider,
        "Provider Account Email": auth.providerAccountEmail,
        "Expiration Date": auth.expirationDate,
        "Is Expired": auth.expirationDate is not None
        and auth.expirationDate < datetime.now(),
    }
    for auth in filtered_authorizations
]

st.info("Select an authorization to view details", icon="👇")

selected = st.dataframe(
    authorization_data,
    column_config={
        "Expiration Date": st.column_config.DatetimeColumn(
            "Expiration Date",
            format="YYYY-MM-DD HH:mm:ss",  # Adjust format as needed
        ),
        "Is Expired": st.column_config.CheckboxColumn(
            "Is Expired",
            help="Indicates if the access token is currently expired",
            width="small",
            disabled=True,  # Make it non-editable
        ),
    },
    hide_index=True,
    use_container_width=True,
    selection_mode="single-row",
    on_select="rerun",
)

if selected["selection"]["rows"]:  # type: ignore
    authorization = filtered_authorizations[selected["selection"]["rows"][0]]  # type: ignore
    assert isinstance(authorization, BackendAuthorization)
    st.session_state.user_id = authorization.userId
    st.session_state.provider_account_id = authorization.providerAccountId
else:
    st.stop()


@st.dialog(title="Delete Authorization")
def delete_authorization_dialog(authorization: BackendAuthorization) -> None:
    if st.button("Confirm Delete", use_container_width=True):
        with st.spinner(
            f"Deleting authorization for {authorization.providerAccountEmail}..."
        ):
            backend_auth_repo.delete_authorization(
                user_id=authorization.userId,
                provider_account_id=authorization.providerAccountId,
            )
            st.success(
                f"Authorization deleted for {authorization.providerAccountEmail}",
                icon="✅",
            )
            data_service.clear_all_caches()
            st.rerun()


st.divider()

st.header("Authorization Details")

st.json(authorization.model_dump())


col1, col2 = st.columns(2)
if col1.button(
    "Test Authorization",
    use_container_width=True,
):
    with st.spinner(
        f"Testing authorization for {authorization.providerAccountEmail}..."
    ):
        try:
            authorization_service.test_authorization(
                user_id=authorization.userId,
                provider_account_id=authorization.providerAccountId,
            )
            st.success(
                f"Authorization is valid for {authorization.providerAccountEmail}",
                icon="✅",
            )
        except Exception as e:
            st.error(
                f"Authorization test failed for {authorization.providerAccountEmail}: {e}",
                icon="❌",
            )
if col2.button(
    "Delete Authorization",
    icon="🗑️",
    use_container_width=True,
):
    delete_authorization_dialog(authorization)
