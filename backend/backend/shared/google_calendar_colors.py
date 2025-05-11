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
        color_map = {
            "lavender": GoogleEventColor.LAVENDER,
            "sage": GoogleEventColor.SAGE,
            "grape": GoogleEventColor.GRAPE,
            "tangerine": GoogleEventColor.TANGERINE,
            "banana": GoogleEventColor.BANANA,
            "flamingo": GoogleEventColor.FLAMINGO,
            "peacock": GoogleEventColor.PEACOCK,
            "graphite": GoogleEventColor.GRAPHITE,
            "blueberry": GoogleEventColor.BLUEBERRY,
            "basil": GoogleEventColor.BASIL,
            "tomato": GoogleEventColor.TOMATO,
        }
        return color_map[color_id]

    def to_color_code(self) -> str:
        m = {
            "lavender": "#a4bdfc",
            "sage": "#7ae7bf",
            "grape": "#dbadff",
            "tangerine": "#ff887c",
            "banana": "#fbd75b",
            "flamingo": "#ffb878",
            "peacock": "#46d6db",
            "graphite": "#e1e1e1",
            "blueberry": "#5484ed",
            "basil": "#51b749",
            "tomato": "#dc2127",
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
