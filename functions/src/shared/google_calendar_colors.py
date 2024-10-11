from enum import Enum


class GoogleEventColor(str, Enum):
    """Represents the colors used in google calendar"""

    # don't use auto() here because it might cause issues with serialization/deserialization
    # e.g if we use auto() and then change the order of the enum values, the deserialization will break
    LAVENDER = "lavender"
    SAGE = "sage"
    GRAPE = "grape"
    TANGERINE = "tangerine"
    BANANA = "banana"
    FLAMINGO = "flamingo"
    PEACOCK = "peacock"
    GRAPHITE = "graphite"
    BLUEBERRY = "blueberry"
    BASIL = "basil"
    TOMATO = "tomato"

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

    def to_color_id(self) -> str:
        match self:
            case GoogleEventColor.LAVENDER:
                return "1"
            case GoogleEventColor.SAGE:
                return "2"
            case GoogleEventColor.GRAPE:
                return "3"
            case GoogleEventColor.TANGERINE:
                return "4"
            case GoogleEventColor.BANANA:
                return "5"
            case GoogleEventColor.FLAMINGO:
                return "6"
            case GoogleEventColor.PEACOCK:
                return "7"
            case GoogleEventColor.GRAPHITE:
                return "8"
            case GoogleEventColor.BLUEBERRY:
                return "9"
            case GoogleEventColor.BASIL:
                return "10"
            case GoogleEventColor.TOMATO:
                return "11"
        raise ValueError(f"Unknown color: {self}")
