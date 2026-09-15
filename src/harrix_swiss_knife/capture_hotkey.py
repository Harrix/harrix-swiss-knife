"""Capture-family hotkeys: short press runs the bound action, long press opens a picker."""

from __future__ import annotations

CAPTURE_HOTKEY_ACTIONS: frozenset[str] = frozenset(
    {
        "OnScreenshotRegion",
        "OnScreenshotRegionClipboard",
        "OnScreenshotRegionKeepWindows",
        "OnScreenshotRegionTranslate",
        "OnRecordRegion",
    },
)

# Hold duration before the capture-action picker opens (ms).
CAPTURE_HOTKEY_LONG_PRESS_MS = 450
