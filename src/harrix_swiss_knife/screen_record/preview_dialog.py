"""Compatibility shim — use `editor_dialog` for the recording editor."""

from __future__ import annotations

from harrix_swiss_knife.screen_record.editor_dialog import (
    RecordingEditorWindow as RecordingPreviewWindow,
)
from harrix_swiss_knife.screen_record.editor_dialog import (
    show_recording_editor as show_recording_preview,
)

__all__ = ["RecordingPreviewWindow", "show_recording_preview"]
