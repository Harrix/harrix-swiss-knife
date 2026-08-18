"""Tests for background icon catalog loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.apps.icons.catalog import CatalogLoadCancelledError, IconCatalog, scan_flat_folder
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
    worker = CatalogLoadWorker(repo, generation=4)
    loaded: list[tuple[object, int]] = []
    failed: list[tuple[str, int]] = []
    worker.succeeded.connect(lambda catalog, gen: loaded.append((catalog, gen)))
    worker.failed.connect(lambda text, gen: failed.append((text, gen)))
    worker.run()
    assert failed == []
    assert len(loaded) == 1
    catalog, generation = loaded[0]
    assert generation == 4
    assert isinstance(catalog, IconCatalog)
    assert catalog.icons[0].id == "building__garage"


def test_catalog_load_worker_reports_missing_folder(tmp_path: Path) -> None:
    worker = CatalogLoadWorker(tmp_path / "missing", generation=2)
    failed: list[tuple[str, int]] = []
    worker.failed.connect(lambda text, gen: failed.append((text, gen)))
    worker.run()
    assert failed
    message, generation = failed[0]
    assert generation == 2
    assert "not found" in message.casefold() or "no svg" in message.casefold() or message


def test_scan_flat_folder_uses_stat_fingerprint(tmp_path: Path) -> None:
    dump = tmp_path / "dump"
    _write(dump / "Infographics" / "chart.svg")
    catalog = scan_flat_folder(dump)
    family = catalog.icons[0]
    assert ":" in family.featured_hash
    assert family.featured_hash == family.variants[0].hash


def test_scan_flat_folder_can_be_cancelled(tmp_path: Path) -> None:
    dump = tmp_path / "dump"
    _write(dump / "one.svg")

    def cancel_immediately() -> bool:
        return True

    with pytest.raises(CatalogLoadCancelledError):
        scan_flat_folder(dump, should_cancel=cancel_immediately)


def test_catalog_load_worker_emits_cancelled(tmp_path: Path) -> None:
    dump = tmp_path / "dump"
    _write(dump / "one.svg")
    worker = CatalogLoadWorker(dump, generation=9)
    worker.request_cancel()
    cancelled: list[int] = []
    worker.cancelled.connect(cancelled.append)
    worker.run()
    assert cancelled == [9]
