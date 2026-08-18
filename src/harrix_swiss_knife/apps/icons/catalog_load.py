"""Load or rebuild an icon catalog outside the GUI thread."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from harrix_swiss_knife.apps.icons.catalog import (
    CatalogLoadCancelledError,
    IconCatalog,
    open_icons_folder,
    rebuild_catalog,
)


class CatalogLoadWorker(QObject):
    """Open or rebuild an icons catalog in a worker thread."""

    succeeded = Signal(object, int)
    failed = Signal(str, int)
    cancelled = Signal(int)
    finished = Signal()

    def __init__(self, path: Path, *, rebuild: bool = False, generation: int = 0) -> None:
        """Store the folder path, rebuild flag, and UI generation token."""
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild
        self.generation = generation
        self._cancel = threading.Event()

    def request_cancel(self) -> None:
        """Ask the running scan to stop at the next checkpoint."""
        self._cancel.set()

    @Slot()
    def run(self) -> None:
        """Load the catalog and report the result."""
        try:
            catalog = (
                rebuild_catalog(self._path, should_cancel=self._cancel.is_set)
                if self._rebuild
                else open_icons_folder(self._path, should_cancel=self._cancel.is_set)
            )
        except CatalogLoadCancelledError:
            self.cancelled.emit(self.generation)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc), self.generation)
        else:
            if self._cancel.is_set():
                self.cancelled.emit(self.generation)
            elif not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result", self.generation)
            else:
                self.succeeded.emit(catalog, self.generation)
        finally:
            self.finished.emit()
