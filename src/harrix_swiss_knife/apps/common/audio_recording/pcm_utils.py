"""PCM / WAV helpers for microphone capture and waveform display."""

from __future__ import annotations

import array
import wave
from typing import TYPE_CHECKING

import harrix_pylib as h
from PySide6.QtMultimedia import QAudioDevice, QAudioFormat

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

if TYPE_CHECKING:
    from pathlib import Path

BYTES_PER_KIB = 1024
BYTES_PER_MIB = 1024 * 1024
LEVEL_GAIN = 2.0
TRIM_SILENCE_THRESHOLD = 700
TRIM_SILENCE_PADDING_S = 0.08
TEMP_MICROPHONE_ID_KEY = "speech_microphone_id"


def audio_device_id(device: QAudioDevice) -> str:
    """Return a stable hex ID for `device`."""
    return device.id().data().hex()


def format_file_size(num_bytes: int) -> str:
    """Return human-readable file size in B, KB, or MB."""
    if num_bytes < BYTES_PER_KIB:
        return f"{num_bytes} B"
    if num_bytes < BYTES_PER_MIB:
        return f"{num_bytes / BYTES_PER_KIB:.1f} KB"
    return f"{num_bytes / BYTES_PER_MIB:.2f} MB"


def format_recording_duration(total_seconds: float) -> str:
    """Return elapsed recording time as `M:SS`."""
    total = max(0, int(total_seconds))
    minutes = total // 60
    seconds = total % 60
    return f"{minutes}:{seconds:02d}"


def load_saved_microphone_id() -> str:
    """Load last used microphone ID from config-temp."""
    try:
        temp_config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return ""
    return str(temp_config.get(TEMP_MICROPHONE_ID_KEY, "")).strip()


def normalize_pcm_to_int16_mono(pcm_data: bytes, audio_format: QAudioFormat) -> bytes:
    """Convert captured PCM to mono int16 suitable for standard WAV files."""
    if not pcm_data:
        return pcm_data

    sample_format = audio_format.sampleFormat()
    channel_count = max(1, audio_format.channelCount())

    if sample_format == QAudioFormat.SampleFormat.Float:
        floats = array.array("f")
        floats.frombytes(pcm_data)
        samples = array.array(
            "h",
            (max(-32768, min(32767, int(sample * 32767.0))) for sample in floats),
        )
    elif sample_format == QAudioFormat.SampleFormat.Int16:
        samples = array.array("h")
        samples.frombytes(pcm_data)
    elif sample_format == QAudioFormat.SampleFormat.Int32:
        ints32 = array.array("i")
        ints32.frombytes(pcm_data)
        samples = array.array("h", (max(-32768, min(32767, sample >> 16)) for sample in ints32))
    elif sample_format == QAudioFormat.SampleFormat.UInt8:
        samples = array.array("h", ((byte - 128) << 8 for byte in pcm_data))
    else:
        return pcm_data

    if channel_count == 1:
        return samples.tobytes()

    mono = array.array("h")
    for index in range(0, len(samples) - channel_count + 1, channel_count):
        mixed = sum(samples[index + channel] for channel in range(channel_count))
        mono.append(int(mixed / channel_count))
    return mono.tobytes()


def pcm_chunk_envelope(pcm_data: bytes, audio_format: QAudioFormat) -> tuple[float, float]:
    """Return normalized negative and positive peaks for a PCM chunk."""
    if not pcm_data:
        return (0.0, 0.0)
    mono_pcm = normalize_pcm_to_int16_mono(pcm_data, audio_format)
    samples = array.array("h")
    samples.frombytes(mono_pcm)
    if not samples:
        return (0.0, 0.0)
    peak_neg = min(samples) / 32768.0
    peak_pos = max(samples) / 32768.0
    peak_neg = max(-1.0, peak_neg * LEVEL_GAIN)
    peak_pos = min(1.0, peak_pos * LEVEL_GAIN)
    return (peak_neg, peak_pos)


def read_wav_pcm(path: Path) -> tuple[tuple[int, int, int, int, str, str], bytes]:
    """Read WAV params and PCM frames from `path`."""
    with wave.open(str(path), "rb") as wav_file:
        params = wav_file.getparams()
        return params, wav_file.readframes(wav_file.getnframes())


def recording_duration_from_pcm(pcm_data: bytes, sample_rate: int) -> float:
    """Return mono int16 PCM duration in seconds."""
    if not pcm_data or sample_rate <= 0:
        return 0.0
    return (len(pcm_data) // 2) / sample_rate


def recording_format_for_device(device: QAudioDevice) -> QAudioFormat:
    """Pick a stable int16 capture format supported by the microphone."""
    for sample_rate, channel_count in ((16000, 1), (44100, 1), (48000, 1), (44100, 2)):
        audio_format = QAudioFormat()
        audio_format.setSampleRate(sample_rate)
        audio_format.setChannelCount(channel_count)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        if device.isFormatSupported(audio_format):
            return audio_format
    return device.preferredFormat()


def save_microphone_id(device: QAudioDevice) -> None:
    """Persist selected microphone ID to config-temp."""
    try:
        temp_config_path = get_temp_config_path()
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
            temp_config_path.write_text("{}", encoding="utf-8")
        h.dev.config_update_value(
            TEMP_MICROPHONE_ID_KEY,
            audio_device_id(device),
            get_config_path_str(),
            is_temp=True,
        )
    except (FileNotFoundError, OSError, ValueError):
        return


def trim_edge_silence_int16_mono(pcm_data: bytes, sample_rate: int) -> bytes:
    """Trim leading/trailing silence from mono int16 PCM using amplitude threshold."""
    if not pcm_data or sample_rate <= 0:
        return pcm_data

    samples = array.array("h")
    samples.frombytes(pcm_data)
    if not samples:
        return pcm_data

    first_sound_idx = -1
    last_sound_idx = -1

    for index, sample in enumerate(samples):
        if abs(sample) > TRIM_SILENCE_THRESHOLD:
            first_sound_idx = index
            break

    if first_sound_idx < 0:
        return pcm_data

    for index in range(len(samples) - 1, -1, -1):
        if abs(samples[index]) > TRIM_SILENCE_THRESHOLD:
            last_sound_idx = index
            break

    if last_sound_idx < first_sound_idx:
        return pcm_data

    pad = int(sample_rate * TRIM_SILENCE_PADDING_S)
    start = max(0, first_sound_idx - pad)
    end = min(len(samples), last_sound_idx + 1 + pad)

    if start == 0 and end == len(samples):
        return pcm_data

    trimmed = array.array("h", samples[start:end])
    return trimmed.tobytes()


def wav_params_from_audio_format(audio_format: QAudioFormat) -> tuple[int, int, int, int, str, str]:
    """Return WAV header params for normalized int16 speech capture."""
    channels = 1 if audio_format.channelCount() > 1 else max(1, audio_format.channelCount())
    return (
        channels,
        2,
        audio_format.sampleRate(),
        0,
        "NONE",
        "not compressed",
    )


def wav_params_match_audio_format(
    wav_params: tuple[int, int, int, int, str, str],
    audio_format: QAudioFormat,
) -> bool:
    """Return whether WAV params match the normalized capture format."""
    expected = wav_params_from_audio_format(audio_format)
    nchannels, sampwidth, framerate, *_rest = wav_params
    return nchannels == expected[0] and sampwidth == expected[1] and framerate == expected[2]


def waveform_buckets_from_pcm(pcm_data: bytes, bucket_count: int) -> list[tuple[float, float]]:
    """Downsample mono int16 PCM to normalized waveform buckets."""
    if bucket_count <= 0:
        return []
    samples = array.array("h")
    samples.frombytes(pcm_data)
    if not samples:
        return [(0.0, 0.0)] * bucket_count

    buckets: list[tuple[float, float]] = []
    sample_count = len(samples)
    for bucket_index in range(bucket_count):
        start = bucket_index * sample_count // bucket_count
        end = (bucket_index + 1) * sample_count // bucket_count
        if start >= end:
            buckets.append((0.0, 0.0))
            continue
        chunk = samples[start:end]
        peak_neg = min(chunk) / 32768.0
        peak_pos = max(chunk) / 32768.0
        buckets.append((peak_neg, peak_pos))
    return buckets


def write_wav(path: Path, params: tuple[int, int, int, int, str, str], pcm_data: bytes) -> None:
    """Write PCM frames to a WAV file."""
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setparams(params)
        wav_file.writeframes(pcm_data)
