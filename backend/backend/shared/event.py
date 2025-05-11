from dataclasses import dataclass

import arrow

from backend.shared.google_calendar_colors import GoogleEventColor


@dataclass(frozen=True)
class Event:
    start: arrow.Arrow
    end: arrow.Arrow
    title: str = ""
    description: str = ""
    location: str = ""
    color: GoogleEventColor | None = None
    is_all_day: bool = False

    def __post_init__(self):
        if self.start is None or self.end is None:
            raise ValueError("Both start and end dates must be provided")
        if self.start >= self.end:
            raise ValueError("Start date must be before end date")

        if self.title is None:
            raise ValueError("Title must be provided")
