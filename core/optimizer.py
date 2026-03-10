"""Core image optimization pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Sequence, Tuple

from PIL import Image, ImageOps

from core.stats import calculate_compression_stats
from utils.file_utils import build_output_path, collect_image_files, ensure_output_dir

PresetSize = Tuple[int, int]


@dataclass(frozen=True)
class OptimizationResult:
    """Outcome of optimizing one image."""

    input_path: Path
    output_path: Path | None
    original_size: int
    optimized_size: int
    compression_percent: float
    status: str
    message: str



def _strip_metadata(image: Image.Image) -> Image.Image:
    """Return a copy of image pixel data without metadata payloads."""
    cleaned = Image.new(image.mode, image.size)
    cleaned.frombytes(image.tobytes())
    return cleaned



def _normalize_mode_for_format(image: Image.Image, image_format: str) -> Image.Image:
    """Adjust color mode for a target export format."""
    target = image_format.upper()

    if target == "JPEG":
        if image.mode in {"RGBA", "LA", "P"}:
            return image.convert("RGB")
        if image.mode != "RGB":
            return image.convert("RGB")

    if target == "PNG":
        if image.mode == "P":
            return image.convert("RGBA")

    if target == "WEBP" and image.mode not in {"RGB", "RGBA"}:
        return image.convert("RGB")

    return image



def _save_to_buffer(image: Image.Image, image_format: str, quality: int) -> bytes:
    """Encode an image to memory and return the payload bytes."""
    buffer = BytesIO()
    image = _normalize_mode_for_format(image, image_format)
    target = image_format.upper()

    if target == "JPEG":
        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
            exif=b"",
        )
    elif target == "PNG":
        compression_level = int(round((100 - quality) / 100 * 9))
        image.save(buffer, format="PNG", optimize=True, compress_level=compression_level)
    elif target == "WEBP":
        image.save(buffer, format="WEBP", quality=quality, method=6)
    else:
        raise ValueError(f"Unsupported output format: {image_format}")

    return buffer.getvalue()



def resize_for_instagram(image: Image.Image, target_size: PresetSize) -> Image.Image:
    """Resize and center-crop an image to exact Instagram preset dimensions."""
    return ImageOps.fit(image, target_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))



def compress_image(image: Image.Image, output_path: Path, quality: int, image_format: str) -> int:
    """Compress and export an image to disk, returning final size in bytes."""
    payload = _save_to_buffer(image, image_format=image_format, quality=quality)
    output_path.write_bytes(payload)
    return len(payload)



def optimize_image(
    input_path: Path,
    output_dir: Path,
    preset_size: PresetSize | None,
    quality: int,
    allow_format_conversion: bool = False,
) -> OptimizationResult:
    """Optimize a single image and export it to output directory."""
    source_path = Path(input_path)
    ensure_output_dir(output_dir)
    original_size = source_path.stat().st_size

    with Image.open(source_path) as opened:
        cleaned = _strip_metadata(opened)
        working_image = resize_for_instagram(cleaned, preset_size) if preset_size else cleaned

        source_ext = source_path.suffix.lower()
        has_alpha = "A" in working_image.getbands()

        if source_ext in {".jpg", ".jpeg"}:
            output_format = "JPEG"
            output_ext = ".jpg"
            payload = _save_to_buffer(working_image, output_format, quality)
        elif source_ext == ".webp":
            output_format = "WEBP"
            output_ext = ".webp"
            payload = _save_to_buffer(working_image, output_format, quality)
        elif source_ext == ".png":
            png_payload = _save_to_buffer(working_image, "PNG", quality)
            if has_alpha or not allow_format_conversion:
                output_format = "PNG"
                output_ext = ".png"
                payload = png_payload
            else:
                jpg_payload = _save_to_buffer(working_image, "JPEG", quality)
                if len(jpg_payload) < len(png_payload):
                    output_format = "JPEG"
                    output_ext = ".jpg"
                    payload = jpg_payload
                else:
                    output_format = "PNG"
                    output_ext = ".png"
                    payload = png_payload
        else:
            raise ValueError(f"Unsupported input format: {source_ext}")

    output_path = build_output_path(source_path, output_dir, output_ext)
    output_path.write_bytes(payload)

    stats = calculate_compression_stats(original_size=original_size, optimized_size=len(payload))

    return OptimizationResult(
        input_path=source_path,
        output_path=output_path,
        original_size=stats.original_size,
        optimized_size=stats.optimized_size,
        compression_percent=stats.compression_percent,
        status="success",
        message=f"Optimized as {output_format}",
    )



def batch_process_images(
    input_paths: Sequence[Path],
    output_dir: Path,
    preset_size: PresetSize | None,
    quality: int,
    allow_format_conversion: bool = False,
) -> list[OptimizationResult]:
    """Batch optimize files from a list of files and/or folders."""
    ensure_output_dir(output_dir)
    files = collect_image_files([Path(item) for item in input_paths])

    results: list[OptimizationResult] = []
    for file_path in files:
        try:
            result = optimize_image(
                input_path=file_path,
                output_dir=output_dir,
                preset_size=preset_size,
                quality=quality,
                allow_format_conversion=allow_format_conversion,
            )
            results.append(result)
        except Exception as exc:  # noqa: BLE001 - keep batch run resilient
            original_size = file_path.stat().st_size if file_path.exists() else 0
            results.append(
                OptimizationResult(
                    input_path=file_path,
                    output_path=None,
                    original_size=original_size,
                    optimized_size=0,
                    compression_percent=0.0,
                    status="failed",
                    message=str(exc),
                )
            )

    return results
