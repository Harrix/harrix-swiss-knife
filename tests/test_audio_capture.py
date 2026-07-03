"""Tests for microphone capture PCM normalization."""

from __future__ import annotations

import array

from PySide6.QtMultimedia import QAudioFormat

from harrix_swiss_knife.apps.common.dialogs.audio_source_dialog import (
    _normalize_pcm_to_int16_mono,
    _wav_params_from_audio_format,
)


def _format(
    *,
    sample_rate: int = 16000,
    channel_count: int = 1,
    sample_format: QAudioFormat.SampleFormat = QAudioFormat.SampleFormat.Int16,
) -> QAudioFormat:
    audio_format = QAudioFormat()
    audio_format.setSampleRate(sample_rate)
    audio_format.setChannelCount(channel_count)
    audio_format.setSampleFormat(sample_format)
    return audio_format


def test_wav_params_use_int16_mono_for_stereo_capture() -> None:
    params = _wav_params_from_audio_format(_format(channel_count=2))
    assert params[:3] == (1, 2, 16000)


def test_normalize_float_pcm_to_int16_mono() -> None:
    floats = array.array("f", [0.0, 0.5, -0.5])
    result = _normalize_pcm_to_int16_mono(floats.tobytes(), _format(sample_format=QAudioFormat.SampleFormat.Float))
    samples = array.array("h")
    samples.frombytes(result)
    assert samples.tolist() == [0, 16383, -16383]


def test_normalize_stereo_int16_downmixes_to_mono() -> None:
    stereo = array.array("h", [1000, 3000, -2000, 2000])
    result = _normalize_pcm_to_int16_mono(
        stereo.tobytes(),
        _format(channel_count=2, sample_format=QAudioFormat.SampleFormat.Int16),
    )
    mono = array.array("h")
    mono.frombytes(result)
    assert mono.tolist() == [2000, 0]
