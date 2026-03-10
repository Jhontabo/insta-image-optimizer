# insta-image-optimizer

A Python application that compresses and optimizes photos for Instagram while preserving visual quality.

## Features

- Supports `JPEG`, `PNG`, and `WEBP`
- Resizes images to Instagram-ready dimensions
- Removes unnecessary metadata during export
- Converts PNG to JPEG when it produces a smaller file and transparency is not required
- Batch processes files and entire folders
- Keeps original files untouched
- Shows per-file and total compression statistics
- Includes both CLI and web interfaces
- FastAPI backend with browser frontend
- Focused on compression without resizing/cropping

## Project Structure

```text
insta-image-optimizer/
│
├── main.py
├── ARCHITECTURE.md
├── web/
│   ├── api.py
│   └── static/index.html
│
├── core/
│   ├── optimizer.py
│   ├── presets.py
│   └── stats.py
│
├── utils/
│   └── file_utils.py
│
├── tests/
│   ├── test_file_utils.py
│   ├── test_optimizer.py
│   ├── test_presets.py
│   └── test_stats.py
│
├── output/
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/Jhontabo/insta-image-optimizer
cd insta-image-optimizer
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Usage

### 1) Web mode (recommended)

Start the API + web UI:

```bash
python3 main.py --web
```

You can also run `python3 main.py` with no input arguments (defaults to web mode).
Then open:

```bash
http://127.0.0.1:8000
```

Custom host/port:

```bash
python3 main.py --web --host 0.0.0.0 --port 8080
```

### 2) CLI mode

Compress one file:

```bash
python3 main.py photos/image1.jpg --quality 90 --output output
```

Optimize multiple files:

```bash
python3 main.py photos/a.jpg photos/b.png photos/c.webp --quality 90
```

Optimize an entire folder recursively:

```bash
python3 main.py photos/ --quality 90 --output optimized_export
```

## Run Tests

```bash
.venv/bin/pytest -q
```

## Key Functions Implemented

- `optimize_image()`
- `compress_image()`
- `calculate_compression_stats()`
- `batch_process_images()`

## Technical Notes

- No resize/crop is applied by default; original dimensions are preserved.
- Compression quality range is `1-100`.
- Metadata is stripped by recreating clean image data before saving.
- PNG files stay as PNG in default mode to preserve visual fidelity.
- Web API endpoint: `POST /api/optimize` (multipart files + quality).
- Web UI includes before/after image previews.
- Download endpoint: `GET /api/download/{job_id}`.

## Target Users

Content creators and photographers who want smaller upload-ready files for Instagram without manually tuning each image.

## License

Open source. Add your preferred license file (for example `MIT`) in the repository root.
