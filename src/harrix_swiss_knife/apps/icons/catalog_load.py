"""Load or rebuild an icon catalog outside the GUI thread."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from harrix_swiss_knife.apps.icons.catalog import IconCatalog, open_icons_folder, rebuild_catalog


class CatalogLoadWorker(QObject):
    """Open or rebuild an icons catalog in a worker thread."""

    succeeded = Signal(object, int)
    failed = Signal(str, int)
    finished = Signal()

    def __init__(self, path: Path, *, rebuild: bool = False, generation: int = 0) -> None:
        """Store the folder path, rebuild flag, and UI generation token."""
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild
        self.generation = generation

    @Slot()
    def run(self) -> None:
        """Load the catalog and report the result."""
        try:
            catalog = rebuild_catalog(self._path) if self._rebuild else open_icons_folder(self._path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc), self.generation)
        else:
            if not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result", self.generation)
            else:
                self.succeeded.emit(catalog, self.generation)
        finally:
            self.finished.emit()
