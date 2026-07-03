"""Speech-oriented audio compression via ffmpeg."""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path


class FfmpegNotFoundError(FileNotFoundError):
    """Raised when ffmpeg.exe is not available in the project root."""


def ffmpeg_exe_path(project_root: Path) -> Path:
    """Return path to ffmpeg.exe under ``project_root``."""
    return project_root / "ffmpeg.exe"


def is_ffmpeg_available(project_root: Path) -> bool:
    """Return True when ffmpeg.exe exists in ``project_root``."""
    return ffmpeg_exe_path(project_root).is_file()


def wav_to_m4a(wav_path: Path, *, project_root: Path) -> Path:
    """Convert WAV to mono 16 kHz AAC m4a for speech transcription.

    Raises:

    - `FfmpegNotFoundError`: When ``ffmpeg.exe`` is missing.
    - `RuntimeError`: When ffmpeg exits with a non-zero status.
    - `OSError`: When input/output paths are invalid.

    """
    ffmpeg = ffmpeg_exe_path(project_root)
    if not ffmpeg.is_file():
        msg = f"ffmpeg.exe not found in {project_root}"
        raise FfmpegNotFoundError(msg)

    m4a_path = wav_path.with_suffix(".m4a")
    args = [
        str(ffmpeg),
        "-i",
        str(wav_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "aac",
        "-b:a",
        "64k",
        "-y",
        str(m4a_path),
    ]
    process = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if process.returncode != 0:
        details = (process.stderr or process.stdout or "").strip()
        msg = details or f"ffmpeg failed: {' '.join(args)}"
        raise RuntimeError(msg)
    return m4a_path


def write_minimal_wav(path: Path, *, duration_sec: float = 0.5, sample_rate: int = 44100) -> None:
    """Write a short silent mono WAV file (for tests)."""
    frame_count = int(sample_rate * duration_sec)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
