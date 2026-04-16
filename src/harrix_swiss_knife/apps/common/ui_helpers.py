"""Small cross-app UI / text helpers.

- `apply_white_editor_background`: set an opaque white background stylesheet
  on inline table editors (so popup delegates don't see through to the row).
- `iter_stripped_non_empty_lines`: iterate over lines of text yielding only
  the non-empty stripped variants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from PySide6.QtWidgets import QWidget


def apply_white_editor_background(editor: QWidget, widget_type_name: str | None = None) -> None:
    """Apply an opaque white background stylesheet to an inline editor widget.

    Args:

    - `editor` (`QWidget`): The editor widget.
    - `widget_type_name` (`str | None`): Explicit Qt widget class selector
      (e.g. `"QComboBox"`). When `None` the actual runtime class name is used.

    """
    selector = widget_type_name or type(editor).__name__
    editor.setStyleSheet(f"{selector} {{ background-color: white; }}")


def enumerate_stripped_non_empty_lines(text: str, start: int = 1) -> Iterator[tuple[int, str]]:
    """Yield `(line_number, stripped_line)` pairs for non-empty lines in `text`.

    Line numbers correspond to positions in the original text (including blank
    lines), so they remain useful for user-facing error messages.

    Args:

    - `text` (`str`): Input text.
    - `start` (`int`): Starting index for the line counter. Defaults to `1`.

    Yields:

    - `tuple[int, str]`: Original 1-based line number and stripped content.

    """
    for line_num, raw_line in enumerate(text.splitlines(), start):
        stripped = raw_line.strip()
        if stripped:
            yield line_num, stripped


def iter_stripped_non_empty_lines(text: str) -> Iterator[str]:
    """Yield stripped, non-empty lines from `text`.

    Args:

    - `text` (`str`): Input text.

    Yields:

    - `str`: Each non-empty stripped line.

    """
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped:
            yield stripped
