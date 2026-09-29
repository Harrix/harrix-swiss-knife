"""Cached font sample previews for the screenshot text toolbar."""

from __future__ import annotations

import hashlib
import logging
import os
import sys
from pathlib import Path

import harrix_pylib as h
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.paths import get_config_path_str

logger = logging.getLogger(__name__)

DEFAULT_FONT_PREVIEW_TEXT = "Example Пример Йё35"  # ignore: HP001
_CONFIG_KEY = "screenshot_font_preview_text"
_PREVIEW_HEIGHT = 28
_PREVIEW_WIDTH = 220
_MEMORY_LIMIT = 256
_FORMAT_VERSION = 1

_ModelIndex = QModelIndex | QPersistentModelIndex

_memory: dict[str, QPixmap] = {}
_memory_order: list[str] = []


class FontPreviewDelegate(QStyledItemDelegate):
    """Paint each font row as family name + sample text in that typeface."""

    def __init__(self, preview_text: str, parent: QWidget | None = None) -> None:
        """Store the sample phrase used for every row."""
        super().__init__(parent)
        self._preview_text = preview_text.strip() or DEFAULT_FONT_PREVIEW_TEXT

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: _ModelIndex) -> None:
        """Draw selection chrome, family label, and cached sample."""
        self.initStyleOption(option, index)
        painter.save()
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())

        family = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        sample = font_preview_pixmap(family, self._preview_text)
        name_rect = QRect(option.rect.left() + 6, option.rect.top(), 120, option.rect.height())
        sample_rect = QRect(
            name_rect.right() + 6,
            option.rect.top() + max(0, (option.rect.height() - sample.height()) // 2),
            sample.width(),
            sample.height(),
        )
        pen = (
            option.palette.highlightedText().color()
            if option.state & QStyle.StateFlag.State_Selected
            else option.palette.text().color()
        )
        painter.setPen(pen)
        ui_font = QFont(option.font)
        ui_font.setPointSizeF(max(8.0, ui_font.pointSizeF()))
        painter.setFont(ui_font)
        painter.drawText(name_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), family)
        painter.drawPixmap(sample_rect.topLeft(), sample)
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: _ModelIndex) -> QSize:  # noqa: ARG002, N802
        """Return a row tall enough for the sample strip."""
        return QSize(max(option.rect.width(), 360), max(_PREVIEW_HEIGHT + 8, 34))


def clear_font_preview_memory() -> None:
    """Drop in-memory previews (disk files stay until phrase/version changes)."""
    _memory.clear()
    _memory_order.clear()


def font_preview_cache_dir(preview_text: str) -> Path:
    """Return the disk folder for the current preview phrase (and pixel size)."""
    digest = hashlib.sha256(
        f"{_FORMAT_VERSION}|{_PREVIEW_WIDTH}x{_PREVIEW_HEIGHT}|{preview_text}".encode()
    ).hexdigest()[:16]
    return _font_preview_root() / digest


def font_preview_pixmap(family: str, preview_text: str | None = None) -> QPixmap:
    """Return a cached sample pixmap for `family`, rendering on first use."""
    text = (preview_text if preview_text is not None else load_font_preview_text()).strip() or DEFAULT_FONT_PREVIEW_TEXT
    family_key = family.strip() or "Sans Serif"
    cache_key = f"{family_key}\0{text}"
    cached = _memory.get(cache_key)
    if cached is not None and not cached.isNull():
        _touch_memory(cache_key)
        return cached

    path = font_preview_cache_dir(text) / f"{_family_file_stem(family_key)}.png"
    if path.is_file():
        loaded = QPixmap(str(path))
        if not loaded.isNull():
            _store_memory(cache_key, loaded)
            return loaded

    pixmap = _render_preview(family_key, text)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(str(path), "PNG")
    except OSError:
        logger.debug("Could not save font preview cache for %s", family_key, exc_info=True)
    _store_memory(cache_key, pixmap)
    return pixmap


def load_font_preview_text() -> str:
    """Return the sample phrase from `config.json`, or the default."""
    try:
        raw = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return DEFAULT_FONT_PREVIEW_TEXT
    if not isinstance(raw, dict):
        return DEFAULT_FONT_PREVIEW_TEXT
    text = str(raw.get(_CONFIG_KEY) or "").strip()
    return text or DEFAULT_FONT_PREVIEW_TEXT


def _family_file_stem(family: str) -> str:
    return hashlib.sha256(family.encode("utf-8")).hexdigest()[:24]


def _font_preview_root() -> Path:
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(local) / "HarrixSwissKnife" / "font_previews"
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "harrix-swiss-knife" / "font_previews"


def _render_preview(family: str, text: str) -> QPixmap:
    pixmap = QPixmap(_PREVIEW_WIDTH, _PREVIEW_HEIGHT)
    pixmap.fill(QColor("#ffffff"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    font = QFont(family)
    font.setPixelSize(16)
    painter.setFont(font)
    painter.setPen(QColor("#222222"))
    painter.drawText(
        pixmap.rect().adjusted(4, 0, -4, 0),
        int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
        text,
    )
    painter.end()
    return pixmap


def _store_memory(key: str, pixmap: QPixmap) -> None:
    _memory[key] = pixmap
    _touch_memory(key)
    while len(_memory_order) > _MEMORY_LIMIT:
        oldest = _memory_order.pop(0)
        _memory.pop(oldest, None)


def _touch_memory(key: str) -> None:
    if key in _memory_order:
        _memory_order.remove(key)
    _memory_order.append(key)
