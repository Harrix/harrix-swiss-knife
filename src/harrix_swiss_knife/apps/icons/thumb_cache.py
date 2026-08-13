"""Disk thumbnail cache for Vector Icons with background hash refresh."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QRectF, Qt, QThread, Signal
from PySide6.QtGui import QImage, QPainter, QPainterPath, QPixmap

from harrix_swiss_knife.apps.icons.vector_render import (
    PREVIEW_BACKGROUND,
    PREVIEW_CORNER_RADIUS_RATIO,
    PREVIEW_ICON_INSET_RATIO,
    render_icon_to_image,
    render_svg_to_image,
    svg_needs_contrast_background,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.icons.catalog import IconCatalog, IconFamily

logger = logging.getLogger(__name__)

DEFAULT_THUMB_SIZE = 160
META_FILENAME = "meta.json"
# Bump when thumbnail raster style changes (forces cache refresh).
THUMB_FORMAT_VERSION = 5

# Re-export preview constants used by tests / callers.
__all__ = [
    "DEFAULT_THUMB_SIZE",
    "PREVIEW_BACKGROUND",
    "PREVIEW_CORNER_RADIUS_RATIO",
    "PREVIEW_ICON_INSET_RATIO",
    "THUMB_FORMAT_VERSION",
    "ThumbnailCache",
    "ThumbnailWorker",
    "default_cache_dir",
    "placeholder_pixmap",
    "render_icon_to_image",
    "render_svg_to_image",
    "start_thumbnail_refresh",
    "svg_needs_contrast_background",
]


class ThumbnailCache:
    """PNG thumbnail store keyed by family ID + featured hash."""

    def __init__(self, cache_dir: Path | None = None, *, size: int = DEFAULT_THUMB_SIZE) -> None:
        """Initialize cache directory and in-memory meta map."""
        self.cache_dir = cache_dir or default_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.size = size
        self._meta: dict[str, dict[str, str | int]] = {}
        self._load_meta()

    def forget(self, family_id: str) -> None:
        """Remove the cached PNG and meta entry for `family_id`."""
        path = self.thumb_path(family_id)
        try:
            if path.is_file():
                path.unlink()
        except OSError:
            logger.warning("Failed to remove thumbnail for %s", family_id)
        self._meta.pop(family_id, None)
        try:
            self.save_meta()
        except OSError:
            logger.warning("Failed to save thumbnail meta after forgetting %s", family_id)

    def is_fresh(self, family: IconFamily) -> bool:
        """Return whether the cached thumb matches the featured hash, size, and format."""
        entry = self._meta.get(family.id)
        path = self.thumb_path(family.id)
        if not entry or not path.is_file():
            return False
        return (
            entry.get("hash") == family.featured_hash
            and int(entry.get("size") or 0) == self.size
            and int(entry.get("format") or 0) == THUMB_FORMAT_VERSION
        )

    def load_pixmap(self, family_id: str) -> QPixmap | None:
        """Load a cached PNG as pixmap when present."""
        path = self.thumb_path(family_id)
        if not path.is_file():
            return None
        pixmap = QPixmap(str(path))
        return None if pixmap.isNull() else pixmap

    def render_and_store(self, family: IconFamily, repo_root: Path) -> QPixmap | None:
        """Render featured icon to PNG cache and return the pixmap."""
        icon_path = family.featured_path(repo_root)
        if icon_path is None and family.variants:
            icon_path = family.variants[0].absolute_path(repo_root, family.folder)
        if icon_path is None:
            return None
        image = render_icon_to_image(icon_path, self.size)
        if image is None:
            return None
        out = self.thumb_path(family.id)
        if not image.save(str(out)):
            logger.warning("Failed to save thumbnail for %s", family.id)
            return None
        self._meta[family.id] = {
            "hash": family.featured_hash,
            "size": self.size,
            "format": THUMB_FORMAT_VERSION,
        }
        return QPixmap.fromImage(image)

    def save_meta(self) -> None:
        """Persist thumbnail metadata to disk."""
        self._meta_path().write_text(json.dumps(self._meta, indent=2) + "\n", encoding="utf-8")

    def stats(self, catalog: IconCatalog | None = None) -> dict[str, int | str]:
        """Collect thumbnail cache statistics for UI display."""
        png_files = [path for path in self.cache_dir.glob("*.png") if path.is_file()]
        total_bytes = 0
        for path in png_files:
            try:
                total_bytes += path.stat().st_size
            except OSError:
                continue

        fresh = 0
        stale = 0
        missing = 0
        catalog_icons = 0
        if catalog is not None:
            catalog_icons = len(catalog.icons)
            for family in catalog.icons:
                if self.is_fresh(family):
                    fresh += 1
                elif self.thumb_path(family.id).is_file():
                    stale += 1
                else:
                    missing += 1

        return {
            "cache_dir": str(self.cache_dir),
            "png_files": len(png_files),
            "total_bytes": total_bytes,
            "meta_entries": len(self._meta),
            "thumb_size": self.size,
            "format_version": THUMB_FORMAT_VERSION,
            "catalog_icons": catalog_icons,
            "fresh": fresh,
            "stale": stale,
            "missing": missing,
        }

    def thumb_path(self, family_id: str) -> Path:
        """Return PNG path for a family ID (safe filename)."""
        safe = family_id.replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe}.png"

    def _load_meta(self) -> None:
        path = self._meta_path()
        if not path.is_file():
            self._meta = {}
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._meta = {}
            return
        self._meta = raw if isinstance(raw, dict) else {}

    def _meta_path(self) -> Path:
        return self.cache_dir / META_FILENAME


class ThumbnailWorker(QObject):
    """Background worker that refreshes stale / missing thumbnails."""

    progress = Signal(str, str)  # family_id, thumb_path
    finished = Signal(int)  # updated count

    def __init__(self, catalog: IconCatalog, cache: ThumbnailCache) -> None:
        """Store catalog/cache references for the worker thread."""
        super().__init__()
        self._catalog = catalog
        self._cache = cache
        self._cancel = False

    def cancel(self) -> None:
        """Request cooperative cancellation."""
        self._cancel = True

    def run(self) -> None:
        """Refresh thumbnails that are missing or have a changed hash."""
        updated = 0
        for family in self._catalog.icons:
            if self._cancel:
                break
            if self._cache.is_fresh(family):
                continue
            try:
                pixmap = self._cache.render_and_store(family, self._catalog.repo_root)
            except (OSError, ValueError, RuntimeError):
                logger.exception("Failed to render thumbnail for %s", family.id)
                continue
            if pixmap is None:
                continue
            updated += 1
            self.progress.emit(family.id, str(self._cache.thumb_path(family.id)))
        if updated:
            self._cache.save_meta()
        self.finished.emit(updated)


def cache_dir_for_root(repo_root: Path | None = None) -> Path:
    """Return thumbnail cache directory, optionally namespaced by folder path."""
    base = default_cache_dir()
    if repo_root is None:
        return base
    digest = hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:12]
    path = base / digest
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_cache_dir() -> Path:
    """Return the per-user thumbnail cache directory."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base = Path(local_app_data) / "HarrixSwissKnife" / "vector_icons_thumbs"
    else:
        base = Path.home() / ".cache" / "HarrixSwissKnife" / "vector_icons_thumbs"
    base.mkdir(parents=True, exist_ok=True)
    return base


def placeholder_pixmap(size: int = DEFAULT_THUMB_SIZE) -> QPixmap:
    """Return a light rounded placeholder tile used before thumbs exist."""
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    radius = max(4.0, size * PREVIEW_CORNER_RADIUS_RATIO)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), radius, radius)
    painter.fillPath(path, PREVIEW_BACKGROUND)
    painter.end()
    return QPixmap.fromImage(image)


def start_thumbnail_refresh(
    catalog: IconCatalog,
    cache: ThumbnailCache,
    *,
    on_progress: object | None = None,
    on_finished: object | None = None,
) -> tuple[QThread, ThumbnailWorker]:
    """Start a QThread that refreshes thumbnails; returns (thread, worker)."""
    thread = QThread()
    worker = ThumbnailWorker(catalog, cache)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    if on_progress is not None:
        worker.progress.connect(on_progress)
    if on_finished is not None:
        worker.finished.connect(on_finished)
    worker.finished.connect(thread.quit)
    thread.finished.connect(worker.deleteLater)
    thread.start()
    return thread, worker
