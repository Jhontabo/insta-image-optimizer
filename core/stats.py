"""Compression statistics helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionStats:
    """Compression information for one optimized file."""

    original_size: int
    optimized_size: int
    bytes_saved: int
    compression_percent: float



def calculate_compression_stats(original_size: int, optimized_size: int) -> CompressionStats:
    """Calculate compression metrics from original and optimized file sizes."""
    if original_size < 0 or optimized_size < 0:
        raise ValueError("File sizes must be non-negative integers")

    bytes_saved = max(original_size - optimized_size, 0)
    if original_size == 0:
        compression_percent = 0.0
    else:
        compression_percent = (bytes_saved / original_size) * 100

    return CompressionStats(
        original_size=original_size,
        optimized_size=optimized_size,
        bytes_saved=bytes_saved,
        compression_percent=round(compression_percent, 2),
    )
