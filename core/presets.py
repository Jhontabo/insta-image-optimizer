"""Instagram image dimension presets."""

from __future__ import annotations

from typing import Dict, Tuple

PresetSize = Tuple[int, int]

INSTAGRAM_PRESETS: Dict[str, PresetSize] = {
    "Square": (1080, 1080),
    "Portrait": (1080, 1350),
    "Landscape": (1080, 566),
    "Story/Reel": (1080, 1920),
}


def get_preset_dimensions(preset_name: str) -> PresetSize:
    """Return (width, height) dimensions for the selected Instagram preset."""
    if preset_name not in INSTAGRAM_PRESETS:
        allowed = ", ".join(INSTAGRAM_PRESETS.keys())
        raise ValueError(f"Unsupported preset '{preset_name}'. Choose one of: {allowed}")
    return INSTAGRAM_PRESETS[preset_name]


def preset_names() -> list[str]:
    """Return available preset names in UI-friendly order."""
    return list(INSTAGRAM_PRESETS.keys())
