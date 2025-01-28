from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

from pydantic import HttpUrl

from functions.synchronizer.google_calendar_manager import (
    GoogleCalendarManager,
)
from functions.services.exceptions.auth import ProviderUserIdMismatchError
from functions.services.exceptions import (
    BaseAuthorizationError,
    UnauthorizedError,
)

from firebase_functions import logger

from functions.models.authorization import BackendAuthorization
from functions.repositories.backend_authorization_repository import (
    IBackendAuthorizationRepository,
)
from functions.settings import settings


class AuthorizationService:
    """
    Handles authorization-related logic, including exchanging authorization codes,
    verifying tokens, storing the results, and returning an authenticated
    Google Calendar API client.
    """

    def __init__(
        self,
        backend_auth_repo: IBackendAuthorizationRepository,
    ) -> None:
        """
        Initialize the AuthorizationService.

        Args:
            backend_auth_repo: (Optional) A repository for storing and retrieving
                               authorization documents.
        """
        self._auth_repo = backend_auth_repo

    def authorize_backend_with_auth_code(
        self,
        *,
        user_id: str,
        auth_code: str,
        redirect_uri: HttpUrl,
        provider_account_id: str,
    ) -> None:
        """
        Exchange the authorization code provided by the frontend for tokens, verify them,
        and store the resulting BackendAuthorization document.

        Args:
            user_id: The Firebase Auth user ID of the user requesting authorization.
            auth_code: The short-lived authorization code returned by OAuth.
            redirect_uri: The redirect URI to which the OAuth provider sends the user.
            provider_account_id: The Google user ID we expect; used to ensure
                                 the correct account is being authorized.

        Raises:
            ValueError: If the token or user ID is not found.
            Exception: For any unexpected error while exchanging or verifying tokens.
        """
        logger.info(f"Authorizing user {user_id} with auth code")

        # Workaround for Google OAuth scope changes
        # https://www.reddit.com/r/webdev/comments/11w1e36/warning_oauth_scope_has_changed_from
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar"],
            redirect_uri=str(redirect_uri),
        )

        try:
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
        except Exception as e:
            raise BaseAuthorizationError(
                message="Error exchanging authorization code",
                original_exception=e,
            )

        assert isinstance(credentials, Credentials)

        if not credentials.id_token:
            raise BaseAuthorizationError("ID token not found in OAuth credentials")

        # The logged-in user can authorize the backend on multiple google accounts.
        # Thus we need to get the unique identifier of the authorized google account (provider_account_id)
        # We can get this from the ID token

        try:
            id_info = verify_oauth2_token(
                credentials.id_token,
                Request(),
                audience=settings.CLIENT_ID,
            )
        except Exception as e:
            raise BaseAuthorizationError(
                message="Error verifying ID token",
                original_exception=e,
            )

        google_user_id = id_info.get("sub")

        if not google_user_id:
            raise BaseAuthorizationError("Google user ID (sub) not found in ID token.")

        if google_user_id != provider_account_id:
            raise ProviderUserIdMismatchError(
                "The authorized Google account does not match the providerAccountId (ProviderUserIdMismatch)"
            )

        if not credentials.token:
            raise BaseAuthorizationError("Token not found in OAuth credentials")

        email = id_info.get("email")
        if not email:
            raise BaseAuthorizationError("Email not found in ID token")

        # Persist the authorization
        self._auth_repo.set_authorization(
            BackendAuthorization(
                userId=user_id,
                provider="google",
                providerAccountId=google_user_id,
                providerAccountEmail=email,
                accessToken=credentials.token,
                refreshToken=credentials.refresh_token,
                expirationDate=credentials.expiry,
            )
        )

        logger.info(f"Successfully authorized user {user_id} for {google_user_id}")

    def get_authenticated_google_calendar_manager(
        self,
        user_id: str,
        provider_account_id: str,
        calendar_id: str,
    ) -> GoogleCalendarManager:
        """
        Get an authenticated GoogleCalendarManager instance for a specific user and calendar.

        This method creates a GoogleCalendarManager with an authenticated Google Calendar service
        for the specified user and calendar. It handles token refresh if needed.

        Args:
            user_id: The Firebase Auth user ID.
            provider_account_id: The Google user ID associated with the calendar access.
            calendar_id: The ID of the Google Calendar to manage.

        Returns:
            GoogleCalendarManager: An authenticated manager instance for the specified calendar.

        Raises:
            UnauthorizedError: If no valid authorization exists for the user/account.
            BaseAuthorizationError: If an error occurs while refreshing the authentication token.
        """
        service = self.get_calendar_service(user_id, provider_account_id)
        return GoogleCalendarManager(service=service, calendar_id=calendar_id)

    def get_calendar_service(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> Any:
        """
        Returns an authenticated instance of the Google Calendar API client
        based on the stored token for this user/provider combination.

        Refreshes the token if it has expired.
        Does not make a request to the Calendar API. Use test_authorization() for that.

        Returns:
            A resource object for interacting with the Google Calendar API.

        Raises:
            UnauthorizedError: If no valid authorization is found for this user/account.
            BaseAuthorizationError: If an error occurs while refreshing the token.
        """
        logger.info(f"Fetching calendar service for {user_id}/{provider_account_id}")

        authorization = self._auth_repo.get_authorization(user_id, provider_account_id)
        if authorization is None:
            raise UnauthorizedError(
                "No valid authorization found for this user/account."
            )

        # Build a Credentials object from stored tokens
        credentials = Credentials(
            client_id=settings.CLIENT_ID,
            token=authorization.accessToken,
            refresh_token=authorization.refreshToken,
            token_uri="https://oauth2.googleapis.com/token",
            client_secret=settings.CLIENT_SECRET,
            expiry=authorization.expirationDate,
        )

        # Potentially refresh tokens if expired
        if not credentials.valid and credentials.refresh_token:
            logger.info("Refreshing Google credentials.")
            try:
                credentials.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing Google credentials: {e}")
                raise BaseAuthorizationError(
                    "Error refreshing Google credentials", original_exception=e
                )

        service = build("calendar", "v3", credentials=credentials)
        return service

    def test_authorization(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> None:
        """
        Performs a lightweight request to ensure the tokens are still valid.

        This can be used to check if the user revoked permissions or if the token expired.

        Args:
            user_id: The Firebase Auth user ID.
            provider_account_id: The Google user ID.

        Raises:
            BaseAuthorizationError: If the authorization is invalid.
        """
        logger.info("Testing authorization with a lightweight Calendar API call.")

        service = self.get_calendar_service(user_id, provider_account_id)

        try:
            # A simple operation that fails if authorization is invalid
            service.calendarList().list().execute(num_retries=2)
            logger.info("Authorization is valid.")

        # TODO : do not catch all exceptions, but only authorization errors
        except Exception as e:
            logger.error(f"Failed to test authorization: {e}")
            raise BaseAuthorizationError(
                "Failed to test authorization",
                original_exception=e,
            )
