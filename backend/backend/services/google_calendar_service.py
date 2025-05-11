from typing import Any
from googleapiclient.errors import HttpError
from firebase_functions import logger
from backend.services.authorization_service import AuthorizationService
from backend.services.exceptions.target_calendar import (
    BaseTargetCalendarError,
)


class GoogleCalendarService:
    def __init__(self, authorization_service: AuthorizationService):
        self._authorization_service = authorization_service

    def list_calendars(
        self,
        user_id: str,
        provider_account_id: str,
        max_calendars: int = 100,
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
            calendars = []
            page_token = None
            while True:
                params = {}
                if page_token:
                    params["pageToken"] = page_token
                calendars_result = service.calendarList().list(**params).execute()
                calendars.extend(calendars_result.get("items", []))
                if len(calendars) >= max_calendars:
                    calendars = calendars[:max_calendars]
                    logger.warn(
                        "Max calendars reached while listing calendars",
                        user_id=user_id,
                        provider_account_id=provider_account_id,
                        max_calendars=max_calendars,
                    )
                    break
                page_token = calendars_result.get("nextPageToken")
                if not page_token:
                    break
            return calendars
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

    def get_calendar_by_id(
        self,
        user_id: str,
        provider_account_id: str,
        calendar_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieves a specific calendarList entry by its ID for the given user/provider account.
        Validates existence but not write access ('owner' or 'writer').

        Returns:
            The calendarList entry object from the Google Calendar API.
            None if the calendar list entry doesn't exist.
        """
        try:
            service = self._authorization_service.get_calendar_service(
                user_id, provider_account_id
            )
            return service.calendars().get(calendarId=calendar_id).execute()
        except HttpError as e:
            # Check if the error is specifically a 404 Not Found
            if e.resp.status == 404:
                logger.warn(
                    f"Calendar not found (404) for ID: {calendar_id}",
                    user_id=user_id,
                    provider_account_id=provider_account_id,
                )
                return None
        except Exception as e:
            logger.error(f"Failed to get calendar by id: {e}")
            raise
