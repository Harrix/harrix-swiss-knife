"""ShareX-like region screenshot capture for Harrix Swiss Knife."""

from harrix_swiss_knife.screenshot.capture import (
    capture_region,
    clear_pending_screen_freeze,
    grab_all_screens,
    prepare_capture_long_press_freeze,
    select_region,
    set_pending_screen_freeze,
    take_pending_screen_freeze,
)

__all__ = [
    "capture_region",
    "clear_pending_screen_freeze",
    "grab_all_screens",
    "prepare_capture_long_press_freeze",
    "select_region",
    "set_pending_screen_freeze",
    "take_pending_screen_freeze",
]
