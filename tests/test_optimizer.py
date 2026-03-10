from pathlib import Path

from PIL import Image

from core.optimizer import batch_process_images, compress_image, optimize_image, resize_for_instagram


def _create_image(path: Path, mode: str = "RGB", size: tuple[int, int] = (1400, 900)) -> None:
    color = (120, 80, 200, 255) if "A" in mode else (120, 80, 200)
    image = Image.new(mode, size, color)
    image.save(path)


def test_resize_for_instagram_returns_exact_size() -> None:
    image = Image.new("RGB", (2000, 1000), (0, 0, 0))
    resized = resize_for_instagram(image, (1080, 1350))
    assert resized.size == (1080, 1350)


def test_compress_image_writes_file(tmp_path: Path) -> None:
    image = Image.new("RGB", (1080, 1080), (220, 100, 30))
    out = tmp_path / "compressed.jpg"
    size = compress_image(image, out, quality=80, image_format="JPEG")

    assert out.exists()
    assert size > 0
    assert out.stat().st_size == size


def test_optimize_image_jpeg_success(tmp_path: Path) -> None:
    source = tmp_path / "input.jpg"
    _create_image(source)

    output_dir = tmp_path / "output"
    result = optimize_image(source, output_dir, (1080, 1080), quality=85)

    assert result.status == "success"
    assert result.output_path is not None
    assert result.output_path.exists()
    assert result.output_path.suffix.lower() in {".jpg", ".jpeg"}
    assert result.optimized_size > 0


def test_optimize_png_with_alpha_keeps_png(tmp_path: Path) -> None:
    source = tmp_path / "alpha.png"
    _create_image(source, mode="RGBA", size=(1080, 1920))

    output_dir = tmp_path / "output"
    result = optimize_image(source, output_dir, (1080, 1920), quality=80)

    assert result.status == "success"
    assert result.output_path is not None
    assert result.output_path.suffix.lower() == ".png"


def test_batch_process_images_handles_failed_file(tmp_path: Path) -> None:
    good = tmp_path / "good.jpg"
    bad = tmp_path / "bad.jpg"

    _create_image(good)
    bad.write_text("not an image")

    results = batch_process_images(
        input_paths=[good, bad],
        output_dir=tmp_path / "output",
        preset_size=(1080, 1080),
        quality=85,
    )

    assert len(results) == 2
    statuses = {result.input_path.name: result.status for result in results}
    assert statuses["good.jpg"] == "success"
    assert statuses["bad.jpg"] == "failed"
