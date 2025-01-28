import pytest

from .google_calendar_colors import GoogleEventColor


def test_color_enum_values() -> None:
    """Test that all expected color enum values exist"""
    assert GoogleEventColor.LAVENDER.value == "lavender"
    assert GoogleEventColor.SAGE.value == "sage"
    assert GoogleEventColor.GRAPE.value == "grape"
    assert GoogleEventColor.TANGERINE.value == "tangerine"
    assert GoogleEventColor.BANANA.value == "banana"
    assert GoogleEventColor.FLAMINGO.value == "flamingo"
    assert GoogleEventColor.PEACOCK.value == "peacock"
    assert GoogleEventColor.GRAPHITE.value == "graphite"
    assert GoogleEventColor.BLUEBERRY.value == "blueberry"
    assert GoogleEventColor.BASIL.value == "basil"
    assert GoogleEventColor.TOMATO.value == "tomato"


def test_from_color_id() -> None:
    """Test conversion from color string to enum"""
    assert GoogleEventColor.from_color_id("lavender") == GoogleEventColor.LAVENDER
    assert GoogleEventColor.from_color_id("sage") == GoogleEventColor.SAGE
    assert GoogleEventColor.from_color_id("tomato") == GoogleEventColor.TOMATO


def test_from_color_id_invalid() -> None:
    """Test that invalid color IDs raise KeyError"""
    with pytest.raises(KeyError):
        GoogleEventColor.from_color_id("invalid_color")


def test_to_color_code() -> None:
    """Test conversion from enum to hex color code"""
    assert GoogleEventColor.LAVENDER.to_color_code() == "#a4bdfc"
    assert GoogleEventColor.SAGE.to_color_code() == "#7ae7bf"
    assert GoogleEventColor.GRAPE.to_color_code() == "#dbadff"
    assert GoogleEventColor.TANGERINE.to_color_code() == "#ff887c"
    assert GoogleEventColor.BANANA.to_color_code() == "#fbd75b"
    assert GoogleEventColor.FLAMINGO.to_color_code() == "#ffb878"
    assert GoogleEventColor.PEACOCK.to_color_code() == "#46d6db"
    assert GoogleEventColor.GRAPHITE.to_color_code() == "#e1e1e1"
    assert GoogleEventColor.BLUEBERRY.to_color_code() == "#5484ed"
    assert GoogleEventColor.BASIL.to_color_code() == "#51b749"
    assert GoogleEventColor.TOMATO.to_color_code() == "#dc2127"


def test_to_color_id() -> None:
    """Test conversion from enum to Google Calendar color ID"""
    assert GoogleEventColor.LAVENDER.to_color_id() == "1"
    assert GoogleEventColor.SAGE.to_color_id() == "2"
    assert GoogleEventColor.GRAPE.to_color_id() == "3"
    assert GoogleEventColor.TANGERINE.to_color_id() == "4"
    assert GoogleEventColor.BANANA.to_color_id() == "5"
    assert GoogleEventColor.FLAMINGO.to_color_id() == "6"
    assert GoogleEventColor.PEACOCK.to_color_id() == "7"
    assert GoogleEventColor.GRAPHITE.to_color_id() == "8"
    assert GoogleEventColor.BLUEBERRY.to_color_id() == "9"
    assert GoogleEventColor.BASIL.to_color_id() == "10"
    assert GoogleEventColor.TOMATO.to_color_id() == "11"
