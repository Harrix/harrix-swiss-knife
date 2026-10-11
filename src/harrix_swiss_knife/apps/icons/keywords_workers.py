"""Background workers for Vector Icons keyword refresh (keep the UI thread free)."""

from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

from harrix_swiss_knife.apps.icons.catalog import (
    IconCatalog,
    iter_families_with_stale_hashes,
    refresh_hashes_for_paths,
    write_catalog_json,
)
from harrix_swiss_knife.apps.icons.vector_render import render_icon_to_image

_DEFAULT_RASTER_SIDE = 768


class KeywordsCatalogCommitWorker(QObject):
    """Refresh file hashes and rewrite `catalog.json` off the UI thread."""

    succeeded = Signal(str)  # family_id
    failed = Signal(str, str)  # family_id, error
    finished = Signal()

    def __init__(self, catalog: IconCatalog, family_id: str, paths: list[Path]) -> None:
        """Store the catalog, family ID, and paths to re-hash."""
        super().__init__()
        self._catalog = catalog
        self._family_id = family_id
        self._paths = list(paths)

    @Slot()
    def run(self) -> None:
        """Hash paths and persist the note catalog."""
        try:
            if self._paths:
                refresh_hashes_for_paths(self._catalog, self._paths)
            write_catalog_json(self._catalog)
            self.succeeded.emit(self._family_id)
        except (OSError, ValueError, TypeError) as exc:
            self.failed.emit(self._family_id, str(exc))
        finally:
            self.finished.emit()


class KeywordsRasterizeWorker(QObject):
    """Rasterize an icon preview for BotHub off the UI thread."""

    succeeded = Signal(object)  # QImage
    failed = Signal(str)
    finished = Signal()

    def __init__(self, icon_path: Path, *, side: int = _DEFAULT_RASTER_SIDE) -> None:
        """Store the icon path and raster side length."""
        super().__init__()
        self._icon_path = Path(icon_path)
        self._side = side

    @Slot()
    def run(self) -> None:
        """Render the icon to a `QImage`."""
        try:
            image = render_icon_to_image(self._icon_path, self._side)
            if image is None or image.isNull():
                self.failed.emit(f"Could not rasterize icon:\n{self._icon_path}")
            else:
                # Detach so the worker thread can finish without sharing the buffer.
                self.succeeded.emit(QImage(image))
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class StaleKeywordsScanWorker(QObject):
    """Find note families whose featured/variant hashes no longer match disk."""

    succeeded = Signal(object, int)  # list[IconFamily], generation
    failed = Signal(str, int)
    cancelled = Signal(int)
    finished = Signal()

    def __init__(self, catalog: IconCatalog, *, limit: int, generation: int = 0) -> None:
        """Store catalog snapshot inputs and a UI generation token."""
        super().__init__()
        self._catalog = catalog
        self._limit = limit
        self.generation = generation
        self._cancel = threading.Event()

    def request_cancel(self) -> None:
        """Ask the scan to stop before emitting results."""
        self._cancel.set()

    @Slot()
    def run(self) -> None:
        """Scan for stale families and report them."""
        try:
            if self._cancel.is_set():
                self.cancelled.emit(self.generation)
                return
            stale = iter_families_with_stale_hashes(self._catalog, limit=self._limit)
            if self._cancel.is_set():
                self.cancelled.emit(self.generation)
                return
            self.succeeded.emit(list(stale), self.generation)
        except (OSError, ValueError, TypeError) as exc:
            self.failed.emit(str(exc), self.generation)
        finally:
            self.finished.emit()


__all__ = [
    "KeywordsCatalogCommitWorker",
    "KeywordsRasterizeWorker",
    "StaleKeywordsScanWorker",
]
