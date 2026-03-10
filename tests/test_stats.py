from core.stats import calculate_compression_stats


def test_calculate_compression_stats_basic() -> None:
    stats = calculate_compression_stats(1000, 400)
    assert stats.original_size == 1000
    assert stats.optimized_size == 400
    assert stats.bytes_saved == 600
    assert stats.compression_percent == 60.0


def test_calculate_compression_stats_zero_original() -> None:
    stats = calculate_compression_stats(0, 0)
    assert stats.bytes_saved == 0
    assert stats.compression_percent == 0.0
