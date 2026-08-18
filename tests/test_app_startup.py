"""Tests for startup diagnostics helpers."""

from __future__ import annotations

from harrix_swiss_knife.app_startup import is_ignored_qt_message


def test_is_ignored_qt_message_filters_svg_noise() -> None:
    assert is_ignored_qt_message(
        r"D:\Dropbox\Graphic\Vector\Background\light (4).svg:1:2004848: Could not resolve property: #aoG"
    )
    assert is_ignored_qt_message("Invalid path data; path truncated.")
    assert is_ignored_qt_message("link #SVGID_1_ is undefined!")
    assert not is_ignored_qt_message("QPainter::begin: Paint device returned engine == 0")
    assert not is_ignored_qt_message("")
