"""Shared dialogs reusable across applications."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.dialogs.ai_source_dialog import AiSourceDialog
from harrix_swiss_knife.apps.common.dialogs.exercise_selection_dialog import ExerciseSelectionDialog
from harrix_swiss_knife.apps.common.dialogs.text_input_dialog import TextInputDialog

__all__ = ["AiSourceDialog", "ExerciseSelectionDialog", "TextInputDialog"]
