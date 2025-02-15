from datetime import datetime, timedelta
from typing import Callable

from firebase_admin import auth
from firebase_admin.auth import UserRecord, UserInfo

from ..models.user import User, UserMetadata, UserProviderData


class FirebaseAuthUserService:
    """Service for managing Firebase users."""

    def __init__(self) -> None:
        """Initialize the UserService."""
        pass

    def _convert_provider_data(self, provider: UserInfo) -> UserProviderData:
        """Convert Firebase UserInfo to UserProviderData.

        Args:
            provider: The Firebase UserInfo to convert

        Returns:
            The converted UserProviderData
        """
        # Firebase UserInfo always has provider_id and uid
        return UserProviderData(
            provider_id=provider.provider_id,
            uid=provider.uid,
            email=provider.email,
            display_name=provider.display_name,
        )

    def _convert_user_record(self, user: UserRecord) -> User:
        """Convert a Firebase UserRecord to our User model.

        Args:
            user: The Firebase UserRecord to convert

        Returns:
            The converted User model
        """
        if user.uid is None:
            raise ValueError("User has no uid")

        return User(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name,
            disabled=user.disabled,
            email_verified=user.email_verified,
            provider_data=[
                self._convert_provider_data(provider) for provider in user.provider_data
            ],
            custom_claims=user.custom_claims,
            user_metadata=UserMetadata(
                creation_timestamp=datetime.fromtimestamp(
                    user.user_metadata.creation_timestamp / 1000
                )
                if user.user_metadata.creation_timestamp
                else None,
                last_sign_in_timestamp=datetime.fromtimestamp(
                    user.user_metadata.last_sign_in_timestamp / 1000
                )
                if user.user_metadata.last_sign_in_timestamp
                else None,
            ),
        )

    def list_all_users(
        self,
        max_results: int = 1000,
        page_token: str | None = None,
        progress_callback: Callable[[list[User], str | None], None] | None = None,
    ) -> tuple[list[User], str | None]:
        """List all Firebase users in the project.

        Args:
            max_results: Maximum number of users to return per page
            page_token: Token for the next page from a previous call
            progress_callback: Optional callback for progress updates, receives the current page of users and next page token

        Returns:
            A tuple containing the list of users and the next page token (if available)
        """
        page = auth.list_users(max_results=max_results, page_token=page_token)
        users = [self._convert_user_record(user) for user in page.users]

        if progress_callback:
            progress_callback(users, page.next_page_token)

        # If there's another page and no callback is provided, recursively fetch all users
        if page.has_next_page and not progress_callback:
            next_page_users, _ = self.list_all_users(
                max_results=max_results, page_token=page.next_page_token
            )
            users.extend(next_page_users)

        return users, page.next_page_token

    def get_recent_signups(
        self, limit: int = 5, max_age_days: int | None = None
    ) -> list[User]:
        """Get the most recent user signups.

        Args:
            limit: Maximum number of recent users to return
            max_age_days: Optional maximum age in days to consider

        Returns:
            List of the most recently signed up users
        """
        all_users, _ = self.list_all_users()

        # Filter users with creation timestamp
        users_with_creation = [
            user
            for user in all_users
            if user.user_metadata.creation_timestamp is not None
        ]

        # Sort by creation timestamp
        sorted_users = sorted(
            users_with_creation,
            key=lambda u: u.user_metadata.creation_timestamp or datetime.min,
            reverse=True,
        )

        # Apply age filter if specified
        if max_age_days is not None:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            sorted_users = [
                user
                for user in sorted_users
                if user.user_metadata.creation_timestamp
                and user.user_metadata.creation_timestamp >= cutoff_date
            ]

        return sorted_users[:limit]
