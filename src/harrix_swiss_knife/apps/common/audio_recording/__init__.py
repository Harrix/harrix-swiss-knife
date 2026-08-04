"""Shared microphone recording widgets and capture helpers."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.audio_recording.buttons import (
    PLAY_BUTTON_GAP,
    RECORD_CAPTION_IDLE_STYLE,
    RECORD_CAPTION_STOP_STYLE,
    ClickableLabel,
    PauseButton,
    PlayButton,
    RecordButton,
    StopPlaybackButton,
)
from harrix_swiss_knife.apps.common.audio_recording.level_widget import AudioLevelWidget
from harrix_swiss_knife.apps.common.audio_recording.pcm_utils import (
    audio_device_id,
    format_file_size,
    format_recording_duration,
    load_saved_microphone_id,
)
from harrix_swiss_knife.apps.common.audio_recording.recorder import FinalizeResult, MicrophoneRecorder, StartResult

__all__ = [
    "PLAY_BUTTON_GAP",
    "RECORD_CAPTION_IDLE_STYLE",
    "RECORD_CAPTION_STOP_STYLE",
    "AudioLevelWidget",
    "ClickableLabel",
    "FinalizeResult",
    "MicrophoneRecorder",
    "PauseButton",
    "PlayButton",
    "RecordButton",
    "StartResult",
    "StopPlaybackButton",
    "audio_device_id",
    "format_file_size",
    "format_recording_duration",
    "load_saved_microphone_id",
]
