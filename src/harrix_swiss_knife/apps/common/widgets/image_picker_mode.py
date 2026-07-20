"""Mode enum for `ImagePicker` (separate module so class sort cannot break import order)."""

from __future__ import annotations

from enum import Enum


class ImagePickerMode(Enum):
    """Display and interaction mode for `ImagePicker`."""

    SINGLE = "single"
    MULTI = "multi"
    COMPACT = "compact"
