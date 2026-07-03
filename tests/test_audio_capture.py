"""Tests for microphone capture PCM normalization."""

from __future__ import annotations

import array

import pytest
from PySide6.QtMultimedia import QAudioFormat, QMediaDevices

from harrix_swiss_knife.apps.common.dialogs.audio_source_dialog import (
    _TEMP_MICROPHONE_ID_KEY,
    _audio_device_id,
    _load_saved_microphone_id,
    _normalize_pcm_to_int16_mono,
    _wav_params_from_audio_format,
    _waveform_buckets_from_pcm,
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


def test_audio_device_id_is_hex_string() -> None:
    device = QMediaDevices.defaultAudioInput()
    if device is None:
        pytest.skip("No default audio input device")
    device_id = _audio_device_id(device)
    assert device_id
    assert all(char in "0123456789abcdef" for char in device_id)


def test_load_saved_microphone_id_reads_config_temp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.dialogs.audio_source_dialog.h.dev.config_load",
        lambda _path, is_temp=False: {_TEMP_MICROPHONE_ID_KEY: "abc123"} if is_temp else {},
    )
    assert _load_saved_microphone_id() == "abc123"


def test_waveform_buckets_from_pcm_tracks_peaks() -> None:
    samples = array.array("h", [0, 16000, -12000, 0, 8000])
    buckets = _waveform_buckets_from_pcm(samples.tobytes(), 3)
    assert len(buckets) == 3
    assert buckets[1][0] < 0
    assert buckets[1][1] > 0
