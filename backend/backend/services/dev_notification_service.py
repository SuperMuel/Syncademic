from abc import ABC, abstractmethod
import requests
import json
import traceback
from firebase_functions import logger
from typing import TypedDict

from backend.models.sync_profile import SyncProfile
from backend.repositories.sync_profile_repository import ISyncProfileRepository
from backend.services.user_service import FirebaseAuthUserService
from backend.settings import settings
from backend.shared import domain_events


class IDevNotificationService(ABC):
    """Interface for developer notification service."""

    @abstractmethod
    def on_new_user(self, domain_event: domain_events.UserCreated) -> None:
        """Notify when a new user is created."""
        pass

    @abstractmethod
    def on_new_sync_profile(
        self, domain_event: domain_events.SyncProfileCreated
    ) -> None:
        """Notify when a new sync profile is created."""
        pass

    @abstractmethod
    def on_sync_failed(
        self,
        domain_event: domain_events.SyncFailed,
    ) -> None:
        """Notify when a synchronization fails."""
        pass

    @abstractmethod
    def on_sync_profile_deletion_failed(
        self,
        domain_event: domain_events.SyncProfileDeletionFailed,
    ) -> None:
        """Notify when a sync profile deletion fails."""
        pass

    @abstractmethod
    def on_ruleset_generation_failed(
        self,
        domain_event: domain_events.RulesetGenerationFailed,
    ) -> None:
        """Notify when a ruleset generation fails."""
        pass

    @abstractmethod
    def on_sync_profile_creation_failed(
        self,
        domain_event: domain_events.SyncProfileCreationFailed,
    ) -> None:
        """Notify when a sync profile creation fails."""
        pass


class NoOpDevNotificationService(IDevNotificationService):
    """No-operation implementation of the notification service."""

    def on_new_user(self, domain_event: domain_events.UserCreated) -> None:
        pass

    def on_new_sync_profile(
        self, domain_event: domain_events.SyncProfileCreated
    ) -> None:
        pass

    def on_sync_failed(
        self,
        domain_event: domain_events.SyncFailed,
    ) -> None:
        pass

    def on_sync_profile_deletion_failed(
        self,
        domain_event: domain_events.SyncProfileDeletionFailed,
    ) -> None:
        pass

    def on_ruleset_generation_failed(
        self,
        domain_event: domain_events.RulesetGenerationFailed,
    ) -> None:
        pass

    def on_sync_profile_creation_failed(
        self,
        domain_event: domain_events.SyncProfileCreationFailed,
    ) -> None:
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
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.user_service = user_service
        self.sync_profile_repo = sync_profile_repo

    def _get_sync_profile(
        self, user_id: str, sync_profile_id: str
    ) -> SyncProfile | None:
        if not self.sync_profile_repo:
            return None
        return self.sync_profile_repo.get_sync_profile(user_id, sync_profile_id)

    def _format_sync_profile(self, sync_profile: SyncProfile | None) -> str:
        if not sync_profile:
            return ""
        return f"Profile Title: <code>{sync_profile.title}</code>\nSchedule Source URL: <code>{sync_profile.scheduleSource.url}</code>"

    def _get_user_info(self, user_id: str) -> _UserInfo | None:
        if not self.user_service:
            return None

        try:
            if not (user := self.user_service.get_user(user_id)):
                logger.warning(
                    f"User not found: {user_id}",
                    user_id=user_id,
                )
                return None
            return {
                "display_name": user.display_name,
                "email": user.email,
            }
        except Exception as e:
            logger.warning(
                f"Error getting user display name: {type(e).__name__}: {str(e)}",
                user_id=user_id,
            )
            return None

    def _format_user_info(self, user_info: _UserInfo | None) -> str:
        if not user_info:
            return ""
        return f"Display Name: <code>{user_info['display_name']}</code>\nEmail: <code>{user_info['email']}</code>"

    def _send_message(self, text: str) -> None:
        """Send a message to the Telegram chat."""
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
            }

            response = requests.post(self.api_url, json=payload, timeout=5.0)

            if not response.ok:
                logger.warning(
                    f"Failed to send Telegram notification: {response.text}"
                )
        except Exception as e:
            logger.warning(f"Error sending Telegram notification: {str(e)}")

    def on_new_user(self, domain_event: domain_events.UserCreated) -> None:
        message = (
            f"🆕 <b>New User Created</b>\nUser ID: <code>{domain_event.user_id}</code>"
        )
        if user_info := self._get_user_info(domain_event.user_id):
            message += f"\n{self._format_user_info(user_info)}"

        self._send_message(message)

    def on_new_sync_profile(
        self, domain_event: domain_events.SyncProfileCreated
    ) -> None:
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

    def on_sync_profile_deletion_failed(
        self,
        domain_event: domain_events.SyncProfileDeletionFailed,
    ) -> None:
        message = (
            f"❌ <b>Sync Profile Deletion Failed</b>\n"
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

    def on_ruleset_generation_failed(
        self,
        domain_event: domain_events.RulesetGenerationFailed,
    ) -> None:
        message = (
            f"❌ <b>Ruleset Generation Failed</b>\n"
            f"User ID: <code>{domain_event.user_id}</code>\n"
            f"Profile ID: <code>{domain_event.sync_profile_id}</code>\n"
        )
        if user_info := self._get_user_info(domain_event.user_id):
            message += f"\n{self._format_user_info(user_info)}"

        if sync_profile := self._get_sync_profile(
            domain_event.user_id, domain_event.sync_profile_id
        ):
            message += f"\n{self._format_sync_profile(sync_profile)}"

        self._send_message(message)

    def on_sync_profile_creation_failed(
        self,
        domain_event: domain_events.SyncProfileCreationFailed,
    ) -> None:
        message = (
            f"❌ <b>Sync Profile Creation Failed</b>\n"
            f"User ID: <code>{domain_event.user_id}</code>\n"
        )
        if user_info := self._get_user_info(domain_event.user_id):
            message += f"\n{self._format_user_info(user_info)}"
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
    """Factory function to create the appropriate notification service based on settings."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured")
        return NoOpDevNotificationService()

    return TelegramDevNotificationService(
        bot_token=settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
        chat_id=settings.TELEGRAM_CHAT_ID,
        user_service=user_service,
        sync_profile_repo=sync_profile_repo,
    )
