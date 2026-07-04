"""Tests for speech audio compression via ffmpeg."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.apps.common.audio_compress import (
    FfmpegNotFoundError,
    audio_file_to_mono_pcm,
    is_ffmpeg_available,
    wav_to_m4a,
    write_minimal_wav,
)


def test_is_ffmpeg_available_false_for_missing_binary(tmp_path: Path) -> None:
    assert not is_ffmpeg_available(tmp_path)


def test_wav_to_m4a_raises_when_ffmpeg_missing(tmp_path: Path) -> None:
    wav_path = tmp_path / "sample.wav"
    write_minimal_wav(wav_path)
    with pytest.raises(FfmpegNotFoundError, match=r"ffmpeg\.exe not found"):
        wav_to_m4a(wav_path, project_root=tmp_path)


@pytest.mark.slow
def test_wav_to_m4a_creates_smaller_m4a(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    if not is_ffmpeg_available(project_root):
        pytest.skip("ffmpeg.exe not available in project root")

    wav_path = tmp_path / "speech.wav"
    write_minimal_wav(wav_path, duration_sec=1.0)

    m4a_path = wav_to_m4a(wav_path, project_root=project_root)

    assert m4a_path.exists()
    assert m4a_path.suffix == ".m4a"
    assert m4a_path.stat().st_size > 0
    assert m4a_path.stat().st_size < wav_path.stat().st_size


def test_audio_file_to_mono_pcm_reads_wav(tmp_path: Path) -> None:
    wav_path = tmp_path / "speech.wav"
    write_minimal_wav(wav_path, duration_sec=0.2)
    pcm = audio_file_to_mono_pcm(wav_path, project_root=tmp_path)
    assert pcm is not None
    assert len(pcm) > 0
