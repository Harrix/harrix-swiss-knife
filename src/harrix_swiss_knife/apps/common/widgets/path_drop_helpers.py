"""Shared drag-and-drop helpers for path-based Qt widgets."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from PySide6.QtGui import QDragEnterEvent, QDropEvent
    from PySide6.QtWidgets import QLineEdit, QWidget


def get_suggested_basename(filename_line_edit: QLineEdit | None, fallback: str) -> str:
    """Return suggested filename stem from a filename field or fallback."""
    if filename_line_edit is None:
        return fallback
    text = filename_line_edit.text().strip()
    if not text:
        return fallback
    size_limit = 200
    safe = re.sub(r'[<>:"/\\|?*]', "_", text).strip(" .") or fallback
    return safe[:size_limit] if len(safe) > size_limit else safe


def install_url_drop_handlers(
    widget: QWidget,
    on_drop_paths: Callable[[list[str]], None],
    *,
    filter_path: Callable[[str], bool] | None = None,
) -> None:
    """Install drag-and-drop handlers that pass local file paths to ``on_drop_paths``."""

    def drag_enter_event(event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(event: QDropEvent) -> None:
        if not event.mimeData().hasUrls():
            return
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if filter_path is not None:
            paths = [path for path in paths if filter_path(path)]
        if paths:
            on_drop_paths(paths)
        event.acceptProposedAction()

    widget.setAcceptDrops(True)
    widget.dragEnterEvent = drag_enter_event  # ty: ignore[invalid-assignment]
    widget.dropEvent = drop_event  # ty: ignore[invalid-assignment]


def unique_path_numbered(folder: Path, base_name: str, suffix: str, width: int = 2) -> Path:
    """Return unused path using ``base_name_01``, ``base_name_02``, ... naming."""
    i = 1
    while True:
        num = str(i).zfill(width)
        path = folder / (f"{base_name}_{num}{suffix}")
        if not path.exists():
            return path
        i += 1
