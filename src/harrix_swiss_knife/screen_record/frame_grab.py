"""Extract a single video frame at a timestamp via ffmpeg (accurate seek)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.audio_compress import ffmpeg_exe_path, is_ffmpeg_available
from harrix_swiss_knife.paths import get_project_root

if TYPE_CHECKING:
    from pathlib import Path


def ffmpeg_frame_grab_args(source: Path, position_ms: int) -> list[str] | None:
    """Build ffmpeg argv that writes one JPEG frame to stdout.

    `-ss` is placed after `-i` so ffmpeg decodes to the exact timestamp instead of
    snapping to the nearest keyframe (important for sparse screen-record GOPs).

    """
    root = get_project_root()
    if not is_ffmpeg_available(root):
        return None
    source = source.resolve()
    if not source.is_file():
        return None
    time_s = max(0, position_ms) / 1000.0
    return [
        str(ffmpeg_exe_path(root)),
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-ss",
        f"{time_s:.3f}",
        "-frames:v",
        "1",
        "-f",
        "mjpeg",
        "-q:v",
        "3",
        "pipe:1",
    ]
