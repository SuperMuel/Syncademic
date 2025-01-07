from typing import Any


class GoogleCalendarService:
    def list_calendars(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> list[dict[str, Any]]:
        """
        Lists all calendars for the given user on the given provider account.
        """

    def create_new_calendar(
        self,
        user_id: str,
        provider_account_id: str,
        summary: str,
        description: str = "",
        color_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Creates a new calendar for the given user/provider account,
        optionally setting a color_id.
        """
