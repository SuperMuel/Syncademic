from dataclasses import dataclass

from enum import Enum
from typing import Optional
import arrow


class GoogleEventColor(Enum):
    """Represents the colors used in google calendar"""

    LAVENDER = "1"
    SAGE = "2"
    GRAPE = "3"
    TANGERINE = "4"
    BANANA = "5"
    FLAMINGO = "6"
    PEACOCK = "7"
    GRAPHITE = "8"
    BLUEBERRY = "9"
    BASIL = "10"
    TOMATO = "11"

    @staticmethod
    def from_color_id(color_id: str) -> "GoogleEventColor":
        if not color_id or not color_id.isdigit() or int(color_id) not in range(1, 12):
            raise ValueError(f"Invalid color id: {color_id}")

        color_map = {
            "1": GoogleEventColor.LAVENDER,
            "2": GoogleEventColor.SAGE,
            "3": GoogleEventColor.GRAPE,
            "4": GoogleEventColor.TANGERINE,
            "5": GoogleEventColor.BANANA,
            "6": GoogleEventColor.FLAMINGO,
            "7": GoogleEventColor.PEACOCK,
            "8": GoogleEventColor.GRAPHITE,
            "9": GoogleEventColor.BLUEBERRY,
            "10": GoogleEventColor.BASIL,
            "11": GoogleEventColor.TOMATO,
        }
        return color_map[color_id]

    def to_color_code(self) -> str:
        m = {
            "1": "a4bdfc",
            "2": "7ae7bf",
            "3": "dbadff",
            "4": "ff887c",
            "5": "fbd75b",
            "6": "ffb878",
            "7": "46d6db",
            "8": "e1e1e1",
            "9": "5484ed",
            "10": "51b749",
            "11": "dc2127",
        }
        return m[self.value]


@dataclass(frozen=True)
class Event:
    start: arrow.Arrow
    end: arrow.Arrow
    title: str = ""
    description: str = ""
    location: str = ""
    color: Optional[GoogleEventColor] = None

    def __post_init__(self):
        if self.start is None or self.end is None:
            raise ValueError("Both start and end dates must be provided")
        if self.start >= self.end:
            raise ValueError("Start date must be before end date")

        if self.title is None:
            raise ValueError("Title must be provided")
