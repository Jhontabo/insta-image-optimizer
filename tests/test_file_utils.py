from pathlib import Path

from utils.file_utils import (
    build_output_path,
    bytes_to_human_readable,
    collect_image_files,
    ensure_output_dir,
    is_optimized_filename,
)


def test_ensure_output_dir(tmp_path: Path) -> None:
    output = tmp_path / "out"
    result = ensure_output_dir(output)
    assert result.exists()
    assert result.is_dir()


def test_collect_image_files_from_file_and_folder(tmp_path: Path) -> None:
    image1 = tmp_path / "a.jpg"
    image2 = tmp_path / "nested" / "b.png"
    optimized = tmp_path / "nested" / "b_optimized.jpg"
    text = tmp_path / "note.txt"

    image1.parent.mkdir(parents=True, exist_ok=True)
    image2.parent.mkdir(parents=True, exist_ok=True)

    image1.write_bytes(b"x")
    image2.write_bytes(b"x")
    optimized.write_bytes(b"x")
    text.write_text("ignore")

    found = collect_image_files([image1, image2.parent, text])
    resolved = {p.resolve() for p in found}

    assert image1.resolve() in resolved
    assert image2.resolve() in resolved
    assert optimized.resolve() not in resolved
    assert text.resolve() not in resolved


def test_build_output_path_makes_unique_name(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    source.write_bytes(b"orig")

    output = tmp_path / "output"
    output.mkdir(parents=True, exist_ok=True)

    first = build_output_path(source, output, ".jpg")
    first.write_bytes(b"done")
    second = build_output_path(source, output, ".jpg")

    assert first.name == "photo_optimized.jpg"
    assert second.name == "photo_optimized_1.jpg"


def test_bytes_to_human_readable() -> None:
    assert bytes_to_human_readable(900) == "900 B"
    assert bytes_to_human_readable(2048) == "2.00 KB"


def test_is_optimized_filename_detects_generated_patterns() -> None:
    assert is_optimized_filename(Path("photo_optimized.jpg"))
    assert is_optimized_filename(Path("photo_optimized_2.png"))
    assert not is_optimized_filename(Path("photo.jpg"))
