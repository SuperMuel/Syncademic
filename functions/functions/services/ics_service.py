from pydantic import HttpUrl


class IcsService:
    def validate_ics_url(self, ics_url: str | HttpUrl) -> tuple[bool, int]:
        """
        1) Fetches the ICS file from the URL (streaming + size checks).
        2) Parses the ICS file to detect if it is valid.
        Returns (is_valid, number_of_events).
        """
        ics_url = HttpUrl(ics_url)

    def fetch_and_parse_ics(
        self,
        ics_url: str,
    ) -> list[Event]:
        """
        Fetch the ICS string, parse it, and return the parsed events.
        Raises an exception if anything fails (fetch or parse).
        """

    def save_ics_to_cache(
        self,
        sync_profile_id: str,
        sync_trigger: str,
        ics_url: str,
        ics_str: str,
        parsing_error: Exception | None = None,
    ) -> None:
        """
        Stores the ICS file in Firebase Storage (or another storage backend),
        along with metadata about the profile, trigger, and any errors.
        """
