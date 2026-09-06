"""Export trimmed screen recordings via ffmpeg (MP4 / GIF / AVIF)."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import harrix_pylib as h

from harrix_swiss_knife.actions.common.subprocess_run import hidden_subprocess_kwargs
from harrix_swiss_knife.apps.common.audio_compress import ffmpeg_exe_path, is_ffmpeg_available
from harrix_swiss_knife.paths import get_project_root

ExportFormat = Literal["mp4", "gif", "avif", "avif_optimized"]

_EXPORT_TIMEOUT = 600.0


@dataclass(frozen=True, slots=True)
class ExportRequest:
    """Parameters for exporting a trimmed recording."""

    source: Path
    destination: Path
    format: ExportFormat
    start_ms: int
    end_ms: int
    remove_audio: bool = False


@dataclass(frozen=True, slots=True)
class ExportResult:
    """Outcome of an export run."""

    ok: bool
    message: str = ""
    path: Path | None = None


def export_recording(request: ExportRequest) -> ExportResult:
    """Trim and re-encode `request.source` to `request.destination`."""
    root = get_project_root()
    if not is_ffmpeg_available(root):
        return ExportResult(ok=False, message="ffmpeg.exe not found in project root")
    source = request.source.resolve()
    if not source.is_file():
        return ExportResult(ok=False, message=f"Source not found:\n{source}")

    start_ms = max(0, request.start_ms)
    end_ms = max(start_ms + 1, request.end_ms)
    start_s = start_ms / 1000.0
    duration_s = (end_ms - start_ms) / 1000.0
    destination = request.destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if request.format == "avif_optimized":
        return _export_avif_optimized(
            source=source,
            destination=destination,
            start_s=start_s,
            duration_s=duration_s,
            root=root,
        )

    ffmpeg = ffmpeg_exe_path(root)
    args = [
        str(ffmpeg),
        "-hide_banner",
        "-y",
        "-ss",
        f"{start_s:.3f}",
        "-t",
        f"{duration_s:.3f}",
        "-i",
        str(source),
    ]
    if request.format == "mp4":
        args.extend(_mp4_args(remove_audio=request.remove_audio))
    elif request.format == "gif":
        args.extend(_gif_args())
    else:
        args.extend(_avif_args())
    args.append(str(destination))

    return _run_ffmpeg(args, destination)


def _avif_args() -> list[str]:
    return [
        "-an",
        "-vf",
        "fps=12,scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v",
        "libaom-av1",
        "-crf",
        "32",
        "-cpu-used",
        "6",
        "-pix_fmt",
        "yuv420p",
    ]


def _export_avif_optimized(
    *,
    source: Path,
    destination: Path,
    start_s: float,
    duration_s: float,
    root: Path,
) -> ExportResult:
    """Trim to a temp MP4, then optimize to AVIF like Images → Optimize (`OnOptimize`)."""
    ffmpeg = ffmpeg_exe_path(root)
    with tempfile.TemporaryDirectory(prefix="hsk_record_avif_") as temp_dir:
        temp_mp4 = Path(temp_dir) / f"{destination.stem}.mp4"
        args = [
            str(ffmpeg),
            "-hide_banner",
            "-y",
            "-ss",
            f"{start_s:.3f}",
            "-t",
            f"{duration_s:.3f}",
            "-i",
            str(source),
            *_mp4_args(remove_audio=True),
            str(temp_mp4),
        ]
        trim = _run_ffmpeg(args, temp_mp4)
        if not trim.ok:
            return ExportResult(ok=False, message=trim.message or "Failed to trim recording before AVIF optimize")

        try:
            message = h.img.optimize_image_with_tools(
                temp_mp4,
                destination,
                project_root=root,
                quality=False,
                max_size=None,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            return ExportResult(ok=False, message=str(exc))

        if not destination.is_file() or destination.stat().st_size <= 0:
            detail = (message or "").strip()
            return ExportResult(ok=False, message=detail or "AVIF optimize produced no output")
        return ExportResult(ok=True, path=destination, message=message or str(destination))


def _gif_args() -> list[str]:
    # Single-pass palette in one filter graph (good enough for screen recordings).
    return [
        "-an",
        "-vf",
        (
            "fps=12,scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=lanczos,split[s0][s1];"
            "[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5"
        ),
    ]


def _mp4_args(*, remove_audio: bool) -> list[str]:
    args = [
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
    ]
    if remove_audio:
        args.append("-an")
    else:
        args.extend(["-c:a", "aac", "-b:a", "128k"])
    return args


def _run_ffmpeg(args: list[str], destination: Path) -> ExportResult:
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_EXPORT_TIMEOUT,
            **hidden_subprocess_kwargs(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return ExportResult(ok=False, message=str(exc))

    if completed.returncode != 0 or not destination.is_file() or destination.stat().st_size <= 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        return ExportResult(ok=False, message=detail[-2000:] or f"ffmpeg failed ({completed.returncode})")
    return ExportResult(ok=True, path=destination, message=str(destination))
