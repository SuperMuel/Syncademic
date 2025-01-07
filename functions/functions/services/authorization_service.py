from typing import Any


class AuthorizationService:
    def authorize_backend(
        self,
        user_id: str,
        auth_code: str,
        redirect_uri: str,
        provider_account_id: str,
    ) -> None:
        """
        Exchange the authorization code for tokens, verify them,
        and store the resulting BackendAuthorization document.
        """

    def is_authorized(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> bool:
        """
        Returns whether the given user is authorized with the specified
        provider account (e.g., Google) in Firestore.
        """
        pass

    def get_calendar_service(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> Any:
        """
        Returns an authenticated instance of the Google Calendar API client
        based on the stored token for this user/provider combination.
        Raises an exception if authorization is missing or invalid.
        """
        pass

    def test_authorization(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> None:
        """
        Performs a lightweight request to ensure the tokens are still valid.
        """
