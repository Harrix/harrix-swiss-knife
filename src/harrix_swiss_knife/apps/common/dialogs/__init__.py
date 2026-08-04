"""Shared dialogs reusable across applications and actions."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.dialogs.ai_source_dialog import AiSourceDialog
from harrix_swiss_knife.apps.common.dialogs.audio_source_dialog import AudioSourceDialog
from harrix_swiss_knife.apps.common.dialogs.exercise_selection_dialog import ExerciseSelectionDialog
from harrix_swiss_knife.apps.common.dialogs.simple_recording_dialog import SimpleRecordingDialog
from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import TextImageSourceDialog
from harrix_swiss_knife.apps.common.dialogs.text_input_dialog import TextInputDialog

__all__ = [
    "AiSourceDialog",
    "AudioSourceDialog",
    "ExerciseSelectionDialog",
    "SimpleRecordingDialog",
    "TextImageSourceDialog",
    "TextInputDialog",
]
