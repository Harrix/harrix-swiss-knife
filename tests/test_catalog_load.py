"""Tests for background icon catalog loading."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.catalog import IconCatalog
from harrix_swiss_knife.apps.icons.catalog_load import CatalogLoadWorker

_MIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#336699"/></svg>'
)


def _write(path: Path, text: str = _MIN_SVG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo_with_garage(tmp_path: Path) -> Path:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "building" / "building__garage"
    _write(note / "featured-image.svg")
    (note / "building__garage.md").write_text(
        "---\ncategories:\n  - building\nlang: en\n---\n\n# Garage\n",
        encoding="utf-8",
    )
    return repo


def test_catalog_load_worker_opens_note_repo(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    worker = CatalogLoadWorker(repo)
    loaded: list[object] = []
    failed: list[str] = []
    worker.succeeded.connect(loaded.append)
    worker.failed.connect(failed.append)
    worker.run()
    assert failed == []
    assert len(loaded) == 1
    catalog = loaded[0]
    assert isinstance(catalog, IconCatalog)
    assert catalog.icons[0].id == "building__garage"


def test_catalog_load_worker_reports_missing_folder(tmp_path: Path) -> None:
    worker = CatalogLoadWorker(tmp_path / "missing")
    failed: list[str] = []
    worker.failed.connect(failed.append)
    worker.run()
    assert failed
    assert "not found" in failed[0].casefold() or "no svg" in failed[0].casefold() or failed[0]
