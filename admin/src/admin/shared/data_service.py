from datetime import datetime

import streamlit as st

from backend.models.authorization import BackendAuthorization
from backend.models.sync_profile import SyncProfile, SyncProfileStatusType
from backend.models.user import User
from backend.repositories.backend_authorization_repository import (
    FirestoreBackendAuthorizationRepository,
)
from backend.repositories.sync_profile_repository import (
    FirestoreSyncProfileRepository,
)
from backend.services.authorization_service import AuthorizationService
from backend.services.user_service import FirebaseAuthUserService


class AdminDataService:
    """Centralized data service for the admin panel."""

    def __init__(self) -> None:
        """Initialize the data service with all required repositories and services."""
        self.user_service = FirebaseAuthUserService()
        self.sync_profile_repo = FirestoreSyncProfileRepository()
        self.backend_auth_repo = FirestoreBackendAuthorizationRepository()
        self.authorization_service = AuthorizationService(
            backend_auth_repo=self.backend_auth_repo
        )

    @st.cache_data(ttl=60, show_spinner="Fetching users...")
    def get_all_users(_self) -> dict[str, User]:
        """Get all users with their data."""
        print("Getting all users")
        users, _ = _self.user_service.list_all_users()
        return {user.uid: user for user in users}

    def get_recent_signups(self, n: int = 10) -> list[User]:
        """Get the n most recent user signups."""
        print("Getting recent signups")
        all_users = self.get_all_users()
        return sorted(
            all_users.values(),
            key=lambda x: x.user_metadata.creation_timestamp or datetime.min,
            reverse=True,
        )[:n]

    @st.cache_data(ttl=60, show_spinner="Fetching sync profiles...")
    def get_all_sync_profiles(_self) -> list[SyncProfile]:
        """Get all valid sync profiles."""
        print("Getting all sync profiles")
        return _self.sync_profile_repo.list_all_sync_profiles()

    @st.cache_data(ttl=60, show_spinner="Fetching authorizations...")
    def get_all_authorizations(_self) -> list[BackendAuthorization]:
        """Fetches all backend authorizations from Firestore."""
        print("Fetching all backend authorizations from Firestore")
        return _self.backend_auth_repo.list_all_authorizations()

    def get_sync_profile_stats(_self) -> dict[str, int]:
        """Get statistics about sync profiles."""
        profiles = _self.get_all_sync_profiles()
        return {
            "total": len(profiles),
            "failed": len(
                [p for p in profiles if p.status.type == SyncProfileStatusType.FAILED]
            ),
            "in_progress": len(
                [
                    p
                    for p in profiles
                    if p.status.type == SyncProfileStatusType.IN_PROGRESS
                ]
            ),
        }

    def clear_all_caches(self) -> None:
        """Clear all cached data."""
        self.get_all_users.clear()
        self.get_all_sync_profiles.clear()
        self.get_all_authorizations.clear()

    def get_sync_profile(self, sync_profile_id: str) -> SyncProfile | None:
        """Get a sync profile by ID."""
        all_sync_profiles = self.get_all_sync_profiles()
        return next((p for p in all_sync_profiles if p.id == sync_profile_id), None)


# Create a singleton instance
data_service = AdminDataService()
