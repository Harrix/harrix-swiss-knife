"""Shared drag-and-drop helpers for path-based Qt widgets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QLineEdit, QWidget


_NUMBERED_STEM_RE = re.compile(r"^(.+)_(\d{2,})$")
_ISO_DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_ISO_DATE_ANYWHERE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_DOT_DATE_RE = re.compile(r"(\d{4})\.(\d{2})\.(\d{2})")
_COMPACT_DATE_RE = re.compile(r"(\d{4})(\d{2})(\d{2})")
_ISO_DATE_PART_COUNT = 3
_MIN_YEAR = 1900
_MAX_YEAR = 2100
_MIN_MONTH = 1
_MAX_MONTH = 12
_MIN_DAY = 1
_MAX_DAY = 31


class _UrlDropEventFilter(QObject):
    """Accept local file URL drops, including on item-view viewports."""

    def __init__(
        self,
        parent: QWidget,
        on_drop_paths: Callable[[list[str]], None],
        *,
        filter_path: Callable[[str], bool] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_drop_paths = on_drop_paths
        self._filter_path = filter_path

    def eventFilter(self, _watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle drag-enter, drag-move, and drop for file URLs."""
        event_type = event.type()
        if event_type == QEvent.Type.DragEnter and isinstance(event, QDragEnterEvent):
            return self._accept_if_paths(event)
        if event_type == QEvent.Type.DragMove and isinstance(event, QDragMoveEvent):
            return self._accept_if_paths(event)
        if event_type == QEvent.Type.Drop and isinstance(event, QDropEvent):
            return self._handle_drop(event)
        return False

    def _accept_if_paths(self, event: QDragEnterEvent | QDragMoveEvent) -> bool:
        if self._local_paths(event):
            event.acceptProposedAction()
            return True
        event.ignore()
        return False

    def _handle_drop(self, event: QDropEvent) -> bool:
        paths = self._local_paths(event)
        if not paths:
            event.ignore()
            return False
        # Accept before callbacks. A modal dialog inside dropEvent keeps Explorer's OLE drag locked.
        event.acceptProposedAction()
        dropped = list(paths)
        QTimer.singleShot(0, lambda: self._on_drop_paths(dropped))
        return True

    def _local_paths(self, event: QDragEnterEvent | QDragMoveEvent | QDropEvent) -> list[str]:
        mime = event.mimeData()
        if mime is None or not mime.hasUrls():
            return []
        paths = [url.toLocalFile() for url in mime.urls() if url.toLocalFile()]
        if self._filter_path is not None:
            return [path for path in paths if self._filter_path(path)]
        return paths


def extract_date_from_filename(path: str) -> str | None:
    """Return `yyyy-MM-dd` parsed from a filename stem, or `None` if not found."""
    stem = Path(path).stem
    if not stem:
        return None

    prefix_match = _ISO_DATE_PREFIX_RE.match(stem)
    if prefix_match:
        candidate = prefix_match.group(1)
        if _is_valid_iso_date(candidate):
            return candidate

    anywhere_match = _ISO_DATE_ANYWHERE_RE.search(stem)
    if anywhere_match:
        candidate = anywhere_match.group(1)
        if _is_valid_iso_date(candidate):
            return candidate

    dot_match = _DOT_DATE_RE.search(stem)
    if dot_match:
        candidate = f"{dot_match.group(1)}-{dot_match.group(2)}-{dot_match.group(3)}"
        if _is_valid_iso_date(candidate):
            return candidate

    compact_match = _COMPACT_DATE_RE.search(stem)
    if compact_match:
        candidate = f"{compact_match.group(1)}-{compact_match.group(2)}-{compact_match.group(3)}"
        if _is_valid_iso_date(candidate):
            return candidate

    return None


def extract_dates_from_paths(paths: list[str]) -> list[str]:
    """Return sorted unique ISO dates extracted from `paths`."""
    dates: list[str] = []
    seen: set[str] = set()
    for path in paths:
        parsed = extract_date_from_filename(path)
        if parsed and parsed not in seen:
            seen.add(parsed)
            dates.append(parsed)
    return sorted(dates)


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


def infer_image_filename_base(paths: list[str]) -> str | None:
    """Infer shared filename base from existing image paths (strips suffixes such as `_01` and `_02`)."""
    bases: list[str] = []
    for path in paths:
        if not path.strip():
            continue
        stem = Path(path).stem
        match = _NUMBERED_STEM_RE.match(stem)
        bases.append(match.group(1) if match else stem)
    if not bases:
        return None
    unique_bases = set(bases)
    if len(unique_bases) == 1:
        return bases[0]
    return bases[0]


def install_url_drop_handlers(
    widget: QWidget,
    on_drop_paths: Callable[[list[str]], None],
    *,
    filter_path: Callable[[str], bool] | None = None,
) -> None:
    """Install drag-and-drop handlers that pass local file paths to `on_drop_paths`.

    Uses an event filter on the widget and its viewport (for `QAbstractItemView`)
    so `DragOnly` lists still accept files from Explorer.

    """
    drop_filter = _UrlDropEventFilter(widget, on_drop_paths, filter_path=filter_path)
    widget.setAcceptDrops(True)
    widget.installEventFilter(drop_filter)
    viewport = getattr(widget, "viewport", None)
    viewport_widget = viewport() if callable(viewport) else None
    if viewport_widget is not None:
        viewport_widget.setAcceptDrops(True)
        viewport_widget.installEventFilter(drop_filter)
    widget.setProperty("_hsk_url_drop_filter", drop_filter)


def resolve_date_from_image_batch(
    extracted_dates: list[str],
    *,
    overwrite: bool,
    current_is_empty: bool,
) -> str | None:
    """Pick a date to apply from a batch of extracted filename dates."""
    if not extracted_dates:
        return None
    if overwrite:
        return extracted_dates[-1]
    if current_is_empty:
        return extracted_dates[0]
    return None


def slugify_image_filename_base(text: str) -> str:
    """Return a lowercase slug for image filename base (spaces to underscores, specials removed)."""
    cleaned = text.strip().lower()
    if not cleaned:
        return ""
    slug = re.sub(r"[^\w]+", "_", cleaned, flags=re.UNICODE)
    slug = re.sub(r"_+", "_", slug).strip("_")
    size_limit = 200
    return slug[:size_limit] if len(slug) > size_limit else slug


def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path:
    """Return a path in folder that does not exist, using base_name and suffix with _1, _2 if needed."""
    path = folder / (base_name + suffix)
    if not path.exists():
        return path
    i = 1
    while True:
        path = folder / (f"{base_name}_{i}{suffix}")
        if not path.exists():
            return path
        i += 1


def unique_path_numbered(folder: Path, base_name: str, suffix: str, width: int = 2) -> Path:
    """Return unused path using `base_name_01`, `base_name_02`, and so on."""
    i = 1
    while True:
        num = str(i).zfill(width)
        path = folder / (f"{base_name}_{num}{suffix}")
        if not path.exists():
            return path
        i += 1


def _is_valid_iso_date(value: str) -> bool:
    parts = value.split("-")
    if len(parts) != _ISO_DATE_PART_COUNT:
        return False
    try:
        year, month, day = (int(part) for part in parts)
    except ValueError:
        return False
    if year < _MIN_YEAR or year > _MAX_YEAR:
        return False
    if month < _MIN_MONTH or month > _MAX_MONTH:
        return False
    return _MIN_DAY <= day <= _MAX_DAY
