"""Small cross-app UI / text helpers.

- `apply_white_editor_background`: set an opaque white background stylesheet
  on inline table editors (so popup delegates don't see through to the row).
- `iter_stripped_non_empty_lines`: iterate over lines of text yielding only
  the non-empty stripped variants.
- `reveal_in_file_explorer`: open the OS file manager and select a file.
- `set_combo_plain_items`: refill a `QComboBox` only when item texts change.

"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QComboBox

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from PySide6.QtWidgets import QAbstractItemView, QWidget
else:
    from PySide6.QtWidgets import QAbstractItemDelegate, QAbstractItemView


def apply_white_editor_background(editor: QWidget, widget_type_name: str | None = None) -> None:
    """Apply an opaque white background stylesheet to an inline editor widget.

    Args:

    - `editor` (`QWidget`): The editor widget.
    - `widget_type_name` (`str | None`): Explicit Qt widget class selector
      (e.g. `QComboBox`). When `None` the actual runtime class name is used.

    """
    selector = widget_type_name or type(editor).__name__
    editor.setStyleSheet(f"{selector} {{ background-color: white; }}")


def close_table_editor_if_open(view: QAbstractItemView) -> None:
    """Close an open inline cell editor before replacing the table model.

    Args:

    - `view` (`QAbstractItemView`): Table or list view that may have an active editor.

    """
    editor = _active_table_editor(view)
    if editor is None:
        return

    view.closeEditor(editor, QAbstractItemDelegate.EndEditHint.SubmitModelCache)


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


def reveal_in_file_explorer(path: Path | str) -> None:
    """Open the system file manager with `path` selected when possible.

    Raises:

    - `FileNotFoundError`: When `path` does not exist.
    - `OSError`: When the file manager cannot be started.

    """
    target = Path(path).resolve()
    if not target.exists():
        msg = f"Path not found: {target}"
        raise FileNotFoundError(msg)

    if sys.platform == "win32":
        # Trailing comma after /select is required by explorer.exe.
        subprocess.run(
            ["explorer", "/select,", str(target)],  # noqa: S607
            check=False,
        )
        return

    if sys.platform == "darwin":
        subprocess.run(["open", "-R", str(target)], check=False)  # noqa: S607
        return

    folder = target if target.is_dir() else target.parent
    subprocess.run(["xdg-open", str(folder)], check=False)  # noqa: S607


def set_combo_plain_items(
    combo: QComboBox,
    items: Sequence[str],
    *,
    leading_empty: bool = False,
    select: str | None = None,
    block_signals: bool = True,
) -> bool:
    """Replace plain-text combo items only when the list actually changes.

    Skips `clear()` when `combo` already shows the same texts, which avoids
    visible flicker from double populate on app open / refresh. Optionally
    selects `select` (or keeps the current text when `select` is `None`).

    Args:

    - `combo` (`QComboBox`): Target combo.
    - `items` (`Sequence[str]`): Item labels after an optional leading empty.
    - `leading_empty` (`bool`): When `True`, prepend an empty "" item.
    - `select` (`str | None`): Text to select after update. When `None`, keep
      the previous `currentText` if it still exists.
    - `block_signals` (`bool`): Block `currentIndexChanged` during mutation.

    Returns:

    - `bool`: `True` when items were cleared and rebuilt.

    """
    desired = ["", *list(items)] if leading_empty else list(items)
    current = [combo.itemText(i) for i in range(combo.count())]
    selection = combo.currentText() if select is None else select

    def _apply_selection() -> None:
        if not selection:
            if combo.currentIndex() != 0 and combo.count() > 0 and combo.itemText(0) == "":
                combo.setCurrentIndex(0)
            return
        index = combo.findText(selection)
        if index >= 0 and combo.currentIndex() != index:
            combo.setCurrentIndex(index)

    if current == desired:
        if block_signals:
            combo.blockSignals(True)  # noqa: FBT003
        try:
            _apply_selection()
        finally:
            if block_signals:
                combo.blockSignals(False)  # noqa: FBT003
        return False

    combo.setUpdatesEnabled(False)
    if block_signals:
        combo.blockSignals(True)  # noqa: FBT003
    try:
        combo.clear()
        if leading_empty:
            combo.addItem("")
            combo.addItems(list(items))
        else:
            combo.addItems(list(items))
        _apply_selection()
    finally:
        if block_signals:
            combo.blockSignals(False)  # noqa: FBT003
        combo.setUpdatesEnabled(True)
    return True


def _active_table_editor(view: QAbstractItemView) -> QWidget | None:
    """Return the open inline cell editor, or `None` if the view is not editing."""
    if view.state() != QAbstractItemView.State.EditingState:
        return None

    index = view.currentIndex()
    if index.isValid():
        # Permanent widgets from setIndexWidget (not temporary delegate editors).
        editor = view.indexWidget(index)
        if editor is not None:
            return editor

    # Temporary QAbstractItemDelegate editors are focus children, not index widgets.
    focus = view.focusWidget()
    if focus is not None and focus is not view:
        return focus
    return None
