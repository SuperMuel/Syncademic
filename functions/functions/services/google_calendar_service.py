from typing import Any
from firebase_functions import logger
from functions.services.authorization_service import AuthorizationService
from functions.services.exceptions.target_calendar import (
    BaseTargetCalendarError,
)


class GoogleCalendarService:
    def __init__(self, authorization_service: AuthorizationService):
        self._authorization_service = authorization_service

    def list_calendars(
        self,
        user_id: str,
        provider_account_id: str,
    ) -> list[dict[str, Any]]:
        """
        Lists all calendars for the given user on the given provider account.

        Returns:
            List of calendar objects from the Google Calendar API

        Raises:
            BaseTargetCalendarError: If the API call fails
        """
        try:
            service = self._authorization_service.get_calendar_service(
                user_id, provider_account_id
            )
            # TODO: handle pagination
            calendars_result = service.calendarList().list().execute()
            return calendars_result.get("items", [])
        except Exception as e:
            logger.error(f"Failed to list calendars: {e}")
            raise BaseTargetCalendarError(
                message="Failed to list calendars",
                original_exception=e,
            )

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

        Returns:
            The created calendar object from the Google Calendar API

        Raises:
            BaseTargetCalendarError: If calendar creation or color update fails
        """
        try:
            service = self._authorization_service.get_calendar_service(
                user_id, provider_account_id
            )

            calendar_body = {
                "summary": summary,
                "description": description,
            }

            result = service.calendars().insert(body=calendar_body).execute()

            # Calendar color is a property of the calendar list entry
            if color_id is not None:
                try:
                    service.calendarList().patch(
                        calendarId=result.get("id"), body={"colorId": color_id}
                    ).execute()
                except Exception as e:
                    logger.error(f"Failed to set calendar color: {e}")
                    # Don't fail the whole operation if just the color update fails

            return result

        except Exception as e:
            logger.error(f"Failed to create calendar: {e}")
            raise BaseTargetCalendarError(
                message="Failed to create calendar",
                original_exception=e,
            )
