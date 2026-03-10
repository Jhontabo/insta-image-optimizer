"""File and path helpers for image optimization workflows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
OPTIMIZED_STEM_PATTERN = re.compile(r".*_optimized(?:_\d+)?$", re.IGNORECASE)


def ensure_output_dir(output_dir: Path) -> Path:
    """Create output directory if it doesn't exist and return it."""
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def is_supported_image(path: Path) -> bool:
    """Check whether a path is a supported image file."""
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_optimized_filename(path: Path) -> bool:
    """Return True when filename matches generated optimized output naming."""
    return bool(OPTIMIZED_STEM_PATTERN.match(path.stem))


def collect_image_files(paths: Iterable[Path]) -> List[Path]:
    """Collect supported image files from a set of file and folder paths."""
    discovered: list[Path] = []

    for candidate in paths:
        path = Path(candidate)
        if not path.exists():
            continue

        if path.is_file() and is_supported_image(path) and not is_optimized_filename(path):
            discovered.append(path)
            continue

        if path.is_dir():
            for nested in path.rglob("*"):
                if is_supported_image(nested) and not is_optimized_filename(nested):
                    discovered.append(nested)

    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for file_path in discovered:
        resolved = file_path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(file_path)

    return unique


def build_output_path(input_path: Path, output_dir: Path, extension: str) -> Path:
    """Build a unique output path in the output directory for an optimized file."""
    safe_ext = extension if extension.startswith(".") else f".{extension}"
    base_name = f"{input_path.stem}_optimized"
    output_path = output_dir / f"{base_name}{safe_ext}"

    counter = 1
    while output_path.exists():
        output_path = output_dir / f"{base_name}_{counter}{safe_ext}"
        counter += 1

    return output_path


def bytes_to_human_readable(size_bytes: int) -> str:
    """Format bytes as a readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"

    size = float(size_bytes)
    units = ["KB", "MB", "GB"]
    for unit in units:
        size /= 1024.0
        if size < 1024.0:
            return f"{size:.2f} {unit}"

    return f"{size:.2f} TB"
