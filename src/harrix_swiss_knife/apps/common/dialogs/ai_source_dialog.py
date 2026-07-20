"""Backward-compatible re-export of TextImageSourceDialog as AiSourceDialog."""

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import (
    SEND_TO_AI_BUTTON_STYLE,
    AiSourceDialog,
    TextImageSourceDialog,
)

__all__ = ["SEND_TO_AI_BUTTON_STYLE", "AiSourceDialog", "TextImageSourceDialog"]
