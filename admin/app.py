import streamlit as st
from dotenv import load_dotenv
from firebase_admin import initialize_app


load_dotenv()

st.set_page_config(
    page_title="Syncademic Admin Panel",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔑",
)


@st.cache_resource()
def init_firebase():
    initialize_app()


init_firebase()

# --- Page Definitions ---
dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",  # Optional: Customize the page name in the navigation
    icon="🏠",  # Optional: Add an icon
)
users_page = st.Page(
    "pages/users.py",
    title="Users",
    icon="🧑‍🤝‍🧑",
)
sync_profiles_page = st.Page(
    "pages/sync_profiles.py",
    title="Sync Profiles",
    icon="🔄",
)
authorizations_page = st.Page(
    "pages/authorizations.py",
    title="Authorizations",
    icon="🔑",
)
ics_studio_page = st.Page(
    "pages/ics_studio.py",
    title="ICS Studio",
    icon="🐛",
)
ai_studio_page = st.Page(
    "pages/ai_studio.py",
    title="AI Studio",
    icon="🤖",
)

# --- Navigation Configuration ---
pages = [
    dashboard_page,
    users_page,
    sync_profiles_page,
    authorizations_page,
    ics_studio_page,
    ai_studio_page,
]

page = st.navigation(pages)

page.run()
