import pytest

from core.presets import get_preset_dimensions, preset_names


def test_get_preset_dimensions_square() -> None:
    assert get_preset_dimensions("Square") == (1080, 1080)


def test_preset_names_contains_required_entries() -> None:
    names = preset_names()
    assert "Square" in names
    assert "Portrait" in names
    assert "Landscape" in names
    assert "Story/Reel" in names


def test_get_preset_dimensions_invalid_raises() -> None:
    with pytest.raises(ValueError):
        get_preset_dimensions("Invalid")
