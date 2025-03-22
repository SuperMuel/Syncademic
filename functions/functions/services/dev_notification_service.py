from abc import ABC, abstractmethod
import requests
import json
import traceback
from firebase_functions import logger
from typing import Any

from functions.settings import settings


class IDevNotificationService(ABC):
    """Interface for developer notification service."""

    @abstractmethod
    def on_new_user(self, user_id: str, additional_data: dict | None = None) -> None:
        """Notify when a new user is created."""
        pass

    @abstractmethod
    def on_new_sync_profile(
        self, user_id: str, sync_profile_id: str, title: str
    ) -> None:
        """Notify when a new sync profile is created."""
        pass

    @abstractmethod
    def on_sync_failed(
        self,
        user_id: str,
        sync_profile_id: str,
        title: str,
        error: str | Exception,
    ) -> None:
        """Notify when a synchronization fails."""
        pass

    @abstractmethod
    def on_custom_event(self, title: str, message: str) -> None:
        """Send a custom notification."""
        pass


class NoOpDevNotificationService(IDevNotificationService):
    """No-operation implementation of the notification service."""

    def on_new_user(self, user_id: str, additional_data: dict | None = None) -> None:
        pass

    def on_new_sync_profile(
        self, user_id: str, sync_profile_id: str, title: str
    ) -> None:
        pass

    def on_sync_failed(
        self,
        user_id: str,
        sync_profile_id: str,
        title: str,
        error: str | Exception,
    ) -> None:
        pass

    def on_custom_event(self, title: str, message: str) -> None:
        pass


class TelegramDevNotificationService(IDevNotificationService):
    """Telegram implementation of the notification service."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

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
                logger.warn(f"Failed to send Telegram notification: {response.text}")
        except Exception as e:
            logger.warn(f"Error sending Telegram notification: {str(e)}")

    def on_new_user(self, user_id: str, additional_data: dict | None = None) -> None:
        message = f"🆕 <b>New User Created</b>\nUser ID: <code>{user_id}</code>"

        if additional_data:
            # Add each piece of additional data to the message
            message += "\n\n<b>Additional Information:</b>"
            for key, value in additional_data.items():
                # Format the key and value for the notification
                message += f"\n{key}: <code>{value}</code>"

        self._send_message(message)

    def on_new_sync_profile(
        self, user_id: str, sync_profile_id: str, title: str
    ) -> None:
        message = (
            f"📅 <b>New Sync Profile Created</b>\n"
            f"Title: <code>{title}</code>\n"
            f"User ID: <code>{user_id}</code>\n"
            f"Profile ID: <code>{sync_profile_id}</code>"
        )
        self._send_message(message)

    def _format_error(self, error: str | Exception) -> str:
        """Format an error for display in a notification."""
        if isinstance(error, str):
            return error

        # Get the error message and traceback
        error_type = type(error).__name__
        error_msg = str(error)
        tb_str = "".join(traceback.format_tb(error.__traceback__))

        # Telegram has a 4096 character limit for messages
        max_tb_length = settings.TELEGRAM_MAX_TRACEBACK_LENGTH

        if len(tb_str) > max_tb_length:
            # Truncate the traceback if it's too long
            tb_str = f"{tb_str[:max_tb_length]}...\n<i>(traceback truncated due to length)</i>"

        # Format the error details
        return f"{error_type}: {error_msg}\n\nTraceback:\n<code>{tb_str}</code>"

    def on_sync_failed(
        self,
        user_id: str,
        sync_profile_id: str,
        title: str,
        error: str | Exception,
    ) -> None:
        formatted_error = self._format_error(error)
        message = (
            f"❌ <b>Sync Failed</b>\n"
            f"Title: <code>{title}</code>\n"
            f"User ID: <code>{user_id}</code>\n"
            f"Profile ID: <code>{sync_profile_id}</code>\n"
            f"Error: <code>{formatted_error}</code>"
        )
        self._send_message(message)

    def on_custom_event(self, title: str, message: str) -> None:
        formatted_message = f"ℹ️ <b>{title}</b>\n{message}"
        self._send_message(formatted_message)


def create_dev_notification_service() -> IDevNotificationService:
    """Factory function to create the appropriate notification service based on settings."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warn("Telegram credentials not configured")
        return NoOpDevNotificationService()

    return TelegramDevNotificationService(
        bot_token=settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
        chat_id=settings.TELEGRAM_CHAT_ID,
    )
