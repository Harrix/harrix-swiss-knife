"""Export trimmed screen recordings via ffmpeg (MP4 / GIF / AVIF)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from harrix_swiss_knife.actions.common.subprocess_run import hidden_subprocess_kwargs
from harrix_swiss_knife.apps.common.audio_compress import ffmpeg_exe_path, is_ffmpeg_available
from harrix_swiss_knife.paths import get_project_root

if TYPE_CHECKING:
    from pathlib import Path

ExportFormat = Literal["mp4", "gif", "avif"]

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
