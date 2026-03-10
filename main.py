"""CLI entrypoint for insta-image-optimizer."""

from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from core.optimizer import batch_process_images
from utils.file_utils import bytes_to_human_readable


def build_parser() -> argparse.ArgumentParser:
    """Build command line parser."""
    parser = argparse.ArgumentParser(
        description="Compress images while preserving visual quality.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Input image file(s) and/or folder(s)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=90,
        help="Compression quality from 1-100 (higher is better quality)",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory path",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch FastAPI web server",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for web server mode",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for web server mode",
    )
    return parser


def print_results(results: list) -> None:
    """Print optimization summary table for CLI mode."""
    if not results:
        print("No supported images found in the provided inputs.")
        return

    print("\nOptimization results:")
    print("-" * 90)
    print(f"{'File':35} {'Original':>12} {'Optimized':>12} {'Saved':>10} {'Status':>10}")
    print("-" * 90)

    for result in results:
        filename = result.input_path.name[:35]
        original = bytes_to_human_readable(result.original_size)
        optimized = bytes_to_human_readable(result.optimized_size)
        saved = f"{result.compression_percent:.2f}%"
        status = result.status
        print(f"{filename:35} {original:>12} {optimized:>12} {saved:>10} {status:>10}")

    print("-" * 90)


def run_cli(args: argparse.Namespace) -> int:
    """Run batch optimization via CLI arguments."""
    if not args.inputs:
        print("No inputs provided. Use --web mode or pass file/folder paths.")
        return 1

    quality = max(1, min(args.quality, 100))

    results = batch_process_images(
        input_paths=[Path(item) for item in args.inputs],
        output_dir=Path(args.output),
        preset_size=None,
        quality=quality,
        allow_format_conversion=False,
    )

    print_results(results)
    return 0


def run_web(args: argparse.Namespace) -> int:
    """Run FastAPI web server."""
    print(f"Starting web UI on http://{args.host}:{args.port}")
    uvicorn.run("web.api:app", host=args.host, port=args.port, reload=False)
    return 0


def main() -> int:
    """Application entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.web or not args.inputs:
        run_web(args)
        return 0

    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
