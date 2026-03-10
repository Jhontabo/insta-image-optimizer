"""FastAPI server for web-based image optimization."""

from __future__ import annotations

import uuid
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from core.optimizer import OptimizationResult, optimize_image
from utils.file_utils import SUPPORTED_EXTENSIONS, is_optimized_filename

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
STATIC_DIR = APP_DIR / "static"
WEB_OUTPUT_DIR = PROJECT_ROOT / "output" / "web_jobs"

app = FastAPI(title="Insta Image Optimizer API")


def _result_to_dict(result: OptimizationResult, job_id: str) -> dict:
    output_file = result.output_path.name if result.output_path else None
    return {
        "input_file": result.input_path.name,
        "output_file": output_file,
        "original_size": result.original_size,
        "optimized_size": result.optimized_size,
        "compression_percent": round(result.compression_percent, 2),
        "status": result.status,
        "message": result.message,
        "preview_url": f"/api/preview/{job_id}/{output_file}" if output_file else None,
    }


def _build_failed_result(file_name: str, message: str) -> OptimizationResult:
    return OptimizationResult(
        input_path=Path(file_name),
        output_path=None,
        original_size=0,
        optimized_size=0,
        compression_percent=0.0,
        status="failed",
        message=message,
    )


def _build_zip(job_output_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(job_output_dir.glob("*")):
            if file_path.is_file():
                archive.write(file_path, arcname=file_path.name)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/optimize")
def optimize_images(
    files: list[UploadFile] = File(...),
    quality: int = Form(90),
) -> JSONResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    quality = max(1, min(quality, 100))

    job_id = uuid.uuid4().hex
    job_input_dir = WEB_OUTPUT_DIR / job_id / "input"
    job_output_dir = WEB_OUTPUT_DIR / job_id / "optimized"
    job_input_dir.mkdir(parents=True, exist_ok=True)
    job_output_dir.mkdir(parents=True, exist_ok=True)

    results: list[OptimizationResult] = []
    for index, upload in enumerate(files):
        source_name = Path(upload.filename or f"file_{index}").name
        source_ext = Path(source_name).suffix.lower()

        if source_ext not in SUPPORTED_EXTENSIONS:
            results.append(
                _build_failed_result(source_name, f"Unsupported file extension: {source_ext}")
            )
            continue
        if is_optimized_filename(Path(source_name)):
            results.append(
                OptimizationResult(
                    input_path=Path(source_name),
                    output_path=None,
                    original_size=0,
                    optimized_size=0,
                    compression_percent=0.0,
                    status="ignored",
                    message="Skipped: already compressed file name pattern detected.",
                )
            )
            continue

        input_path = job_input_dir / f"{index}_{source_name}"
        payload = upload.file.read()
        input_path.write_bytes(payload)

        try:
            result = optimize_image(
                input_path=input_path,
                output_dir=job_output_dir,
                preset_size=None,
                quality=quality,
                allow_format_conversion=False,
            )
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            failed = OptimizationResult(
                input_path=Path(source_name),
                output_path=None,
                original_size=input_path.stat().st_size if input_path.exists() else 0,
                optimized_size=0,
                compression_percent=0.0,
                status="failed",
                message=str(exc),
            )
            results.append(failed)

    zip_path = WEB_OUTPUT_DIR / f"{job_id}.zip"
    _build_zip(job_output_dir, zip_path)

    total_original = sum(item.original_size for item in results)
    total_optimized = sum(item.optimized_size for item in results)
    success_count = sum(1 for item in results if item.status == "success")
    saved_percent = 0.0
    if total_original > 0:
        saved_percent = ((total_original - total_optimized) / total_original) * 100

    return JSONResponse(
        {
            "job_id": job_id,
            "download_url": f"/api/download/{job_id}",
            "summary": {
                "processed": len(results),
                "success": success_count,
                "saved_percent": round(saved_percent, 2),
            },
            "results": [_result_to_dict(item, job_id=job_id) for item in results],
        }
    )


@app.get("/api/preview/{job_id}/{file_name}")
def preview_file(job_id: str, file_name: str) -> FileResponse:
    job_output_dir = WEB_OUTPUT_DIR / job_id / "optimized"
    candidate = (job_output_dir / file_name).resolve()
    if job_output_dir.resolve() not in candidate.parents:
        raise HTTPException(status_code=400, detail="Invalid file path.")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Preview file not found.")
    return FileResponse(candidate)


@app.get("/api/download/{job_id}")
def download_results(job_id: str) -> FileResponse:
    zip_path = WEB_OUTPUT_DIR / f"{job_id}.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Job not found.")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"optimized_{job_id}.zip",
    )
