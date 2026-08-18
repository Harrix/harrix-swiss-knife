"""Load or rebuild an icon catalog outside the GUI thread."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from harrix_swiss_knife.apps.icons.catalog import IconCatalog, open_icons_folder, rebuild_catalog


class CatalogLoadWorker(QObject):
    """Open or rebuild an icons catalog in a worker thread."""

    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, path: Path, *, rebuild: bool = False) -> None:
        """Store the folder path and whether to force a catalog rebuild."""
        super().__init__()
        self._path = Path(path)
        self._rebuild = rebuild

    @Slot()
    def run(self) -> None:
        """Load the catalog and report the result."""
        try:
            catalog = rebuild_catalog(self._path) if self._rebuild else open_icons_folder(self._path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
            self.failed.emit(str(exc))
        else:
            if not isinstance(catalog, IconCatalog):
                self.failed.emit("Catalog loader returned an unexpected result")
            else:
                self.succeeded.emit(catalog)
        finally:
            self.finished.emit()
