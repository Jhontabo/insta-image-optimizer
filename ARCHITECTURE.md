# insta-image-optimizer Architecture

## Overview
`insta-image-optimizer` is a layered Python web + CLI application for Instagram-focused image compression.

- `core/`: Pure image and statistics logic.
- `utils/`: File discovery, path handling, and formatting helpers.
- `web/`: FastAPI endpoints and static frontend.
- `main.py`: CLI entrypoint and web server bootstrap.

## Module Responsibilities

### `core/presets.py`
- Defines Instagram export presets.
- Validates and returns dimensions from preset names.

### `core/stats.py`
- Calculates and stores compression metrics.
- Provides percentage and byte reduction data.

### `core/optimizer.py`
- Main optimization pipeline.
- Required functions:
  - `resize_for_instagram()`
  - `compress_image()`
  - `optimize_image()`
  - `batch_process_images()`
- Handles metadata stripping and optional PNG-to-JPEG conversion when smaller.

### `utils/file_utils.py`
- Discovers supported image files from paths and folders.
- Creates output folders.
- Builds unique output file paths.
- Formats byte sizes for display.

### `web/api.py`
- FastAPI application:
  - Serves `web/static/index.html`
  - Receives image uploads on `POST /api/optimize`
  - Returns per-file optimization results and summary
  - Exposes ZIP download endpoint: `GET /api/download/{job_id}`

### `main.py`
- CLI prototype:
  - Process one or many paths
  - Choose preset and quality
  - Choose output directory
- Can also launch web mode with `--web`.

## Data Flow
1. User uploads files from browser UI or passes paths via CLI.
2. Web API stores uploads temporarily and validates extensions/preset.
3. `core.optimizer.optimize_image()` processes each image.
4. `core.stats.calculate_compression_stats()` computes metrics.
5. API returns JSON summary and builds downloadable ZIP.
6. Browser or CLI displays per-file results.
