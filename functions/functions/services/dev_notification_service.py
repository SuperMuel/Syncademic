from abc import ABC, abstractmethod
import requests
import json
import traceback
from firebase_functions import logger
from typing import TypedDict

from functions.models.sync_profile import SyncProfile
from functions.repositories.sync_profile_repository import ISyncProfileRepository
from functions.services.user_service import FirebaseAuthUserService
from functions.settings import settings
from functions.shared import domain_events


class IDevNotificationService(ABC):
    """Interface for developer notification service."""

    @abstractmethod
    def on_new_user(self, domain_event: domain_events.UserCreated) -> None:
        """
        Sends a notification about the creation of a new user.
        
        Args:
            domain_event: The event containing details about the newly created user.
        """
        pass

    @abstractmethod
    def on_new_sync_profile(
        self, domain_event: domain_events.SyncProfileCreated
    ) -> None:
        """
        Sends a notification about the creation of a new sync profile.
        
        Args:
            domain_event: The event containing details of the newly created sync profile.
        """
        pass

    @abstractmethod
    def on_sync_failed(
        self,
        domain_event: domain_events.SyncFailed,
    ) -> None:
        """
        Sends a notification about a failed synchronization event.
        
        Args:
        	domain_event: The SyncFailed domain event containing user ID, sync profile ID, error details, and traceback information.
        """
        pass


class NoOpDevNotificationService(IDevNotificationService):
    """No-operation implementation of the notification service."""

    def on_new_user(self, domain_event: domain_events.UserCreated) -> None:
        """
        Handles a new user creation event for developer notifications.
        
        Args:
        	domain_event: The event object containing details about the newly created user.
        """
        pass

    def on_new_sync_profile(
        self, domain_event: domain_events.SyncProfileCreated
    ) -> None:
        """
        Sends a notification about the creation of a new sync profile.
        
        Args:
            domain_event: The event containing details about the newly created sync profile.
        """
        pass

    def on_sync_failed(
        self,
        domain_event: domain_events.SyncFailed,
    ) -> None:
        """
        Sends a developer notification about a sync failure event.
        
        The notification includes user information, sync profile details, and error specifics
        extracted from the provided domain event.
        """
        pass


class _UserInfo(TypedDict):
    display_name: str | None
    email: str | None


class TelegramDevNotificationService(IDevNotificationService):
    """Telegram implementation of the notification service."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        *,
        user_service: FirebaseAuthUserService | None,
        sync_profile_repo: ISyncProfileRepository | None,
    ) -> None:
        """
        Initializes the Telegram developer notification service.
        
        Args:
            bot_token: Telegram bot token for authentication.
            chat_id: Telegram chat ID to send notifications to.
            user_service: Optional user service for retrieving user information.
            sync_profile_repo: Optional repository for accessing sync profile data.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.user_service = user_service
        self.sync_profile_repo = sync_profile_repo

    def _get_sync_profile(
        self, user_id: str, sync_profile_id: str
    ) -> SyncProfile | None:
        """
        Retrieves a sync profile by user ID and sync profile ID if a repository is available.
        
        Returns:
            The sync profile if found; otherwise, None.
        """
        if not self.sync_profile_repo:
            return None
        return self.sync_profile_repo.get_sync_profile(user_id, sync_profile_id)

    def _format_sync_profile(self, sync_profile: SyncProfile | None) -> str:
        """
        Formats sync profile details as an HTML string.
        
        Returns:
            An HTML-formatted string with the sync profile's title and schedule source URL,
            or an empty string if the sync profile is None.
        """
        if not sync_profile:
            return ""
        return f"Profile Title: <code>{sync_profile.title}</code>\nSchedule Source URL: <code>{sync_profile.scheduleSource.url}</code>"

    def _get_user_info(self, user_id: str) -> _UserInfo | None:
        """
        Retrieves user display name and email for the given user ID.
        
        Returns:
            A dictionary with 'display_name' and 'email' if the user exists and can be retrieved; otherwise, None.
        """
        if not self.user_service:
            return None

        try:
            if not (user := self.user_service.get_user(user_id)):
                logger.warn(
                    f"User not found: {user_id}",
                    user_id=user_id,
                )
                return None
            return {
                "display_name": user.display_name,
                "email": user.email,
            }
        except Exception as e:
            logger.warn(
                f"Error getting user display name: {type(e).__name__}: {str(e)}",
                user_id=user_id,
            )
            return None

    def _format_user_info(self, user_info: _UserInfo | None) -> str:
        """
        Formats user information as an HTML string for display in Telegram messages.
        
        Args:
            user_info: A dictionary containing optional 'display_name' and 'email' fields.
        
        Returns:
            An HTML-formatted string with the user's display name and email, or an empty string if user_info is None.
        """
        if not user_info:
            return ""
        return f"Display Name: <code>{user_info['display_name']}</code>\nEmail: <code>{user_info['email']}</code>"

    def _send_message(self, text: str) -> None:
        """
        Sends a message to the configured Telegram chat using the bot API.
        
        Args:
            text: The message content to send, formatted as HTML.
        """
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
            }

            response = requests.post(self.api_url, json=payload, timeout=5.0)

            if not response.ok:
                logger.warn(f"Failed to send Telegram notification: {response.text}")
        except Exception as e:
            logger.warn(f"Error sending Telegram notification: {str(e)}")

    def on_new_user(self, domain_event: domain_events.UserCreated) -> None:
        """
        Sends a Telegram notification about the creation of a new user.
        
        Includes the user ID and, if available, formatted user display name and email.
        """
        message = (
            f"🆕 <b>New User Created</b>\nUser ID: <code>{domain_event.user_id}</code>"
        )
        if user_info := self._get_user_info(domain_event.user_id):
            message += f"\n{self._format_user_info(user_info)}"

        self._send_message(message)

    def on_new_sync_profile(
        self, domain_event: domain_events.SyncProfileCreated
    ) -> None:
        """
        Sends a Telegram notification about the creation of a new sync profile.
        
        Includes user information and sync profile details in the message if available.
        """
        message = (
            f"📅 <b>New Sync Profile Created</b>\n"
            f"User ID: <code>{domain_event.user_id}</code>\n"
            f"Profile ID: <code>{domain_event.sync_profile_id}</code>"
        )
        if user_info := self._get_user_info(domain_event.user_id):
            message += f"\n{self._format_user_info(user_info)}"

        if sync_profile := self._get_sync_profile(
            domain_event.user_id, domain_event.sync_profile_id
        ):
            message += f"\n{self._format_sync_profile(sync_profile)}"

        self._send_message(message)

    def on_sync_failed(
        self,
        domain_event: domain_events.SyncFailed,
    ) -> None:
        """
        Sends a Telegram notification about a sync failure event, including user, profile, and error details.
        
        The message includes user information, sync profile details, error type, error message, and a truncated traceback if available.
        """
        message = (
            f"❌ <b>Sync Failed</b>\n"
            f"User ID: <code>{domain_event.user_id}</code>\n"
            f"Profile ID: <code>{domain_event.sync_profile_id}</code>\n"
        )
        if user_info := self._get_user_info(domain_event.user_id):
            message += f"\n{self._format_user_info(user_info)}"

        if sync_profile := self._get_sync_profile(
            domain_event.user_id, domain_event.sync_profile_id
        ):
            message += f"\n{self._format_sync_profile(sync_profile)}"

        message += f"\nError Type: <code>{domain_event.error_type}</code>"
        message += f"\nError Message: <code>{domain_event.error_message}</code>"
        if domain_event.formatted_traceback:
            message += (
                f"\nTraceback: <code>{domain_event.formatted_traceback[:1000]}</code>"
            )

        self._send_message(message)


def create_dev_notification_service(
    user_service: FirebaseAuthUserService,
    sync_profile_repo: ISyncProfileRepository,
) -> IDevNotificationService:
    """
    Creates a developer notification service instance based on Telegram configuration.
    
    If Telegram bot credentials are configured in settings, returns a Telegram-based
    notification service; otherwise, returns a no-operation implementation.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warn("Telegram credentials not configured")
        return NoOpDevNotificationService()

    return TelegramDevNotificationService(
        bot_token=settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
        chat_id=settings.TELEGRAM_CHAT_ID,
        user_service=user_service,
        sync_profile_repo=sync_profile_repo,
    )
