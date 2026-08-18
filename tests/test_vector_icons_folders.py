"""Tests for Vector Icons folder-tree prefixes and folder filters."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.catalog import (
    CatalogKind,
    IconCatalog,
    IconFamily,
    family_in_folder,
    folder_disk_path,
    folder_parts,
)


def _family(family_id: str, folder: str, *, categories: list[str] | None = None) -> IconFamily:
    return IconFamily(
        id=family_id,
        title=family_id,
        categories=categories or [],
        tags=[],
        folder=folder,
        featured="",
        featured_hash="",
    )


def _catalog(icons: list[IconFamily], *, kind: CatalogKind = "note") -> IconCatalog:
    return IconCatalog(version=1, generated_at="", icons=icons, repo_root=Path(), kind=kind)


def test_folder_disk_path_joins_prefix_or_repo_root(tmp_path: Path) -> None:
    repo = tmp_path / "icons-repo"
    assert folder_disk_path(repo, "") == repo
    assert folder_disk_path(repo, "icons/animals") == repo / "icons" / "animals"
    assert folder_disk_path(repo, r"icons\food") == repo / "icons" / "food"


def test_folder_parts_normalizes_slashes() -> None:
    assert folder_parts(r"icons\animals\cat") == ["icons", "animals", "cat"]
    assert folder_parts("icons/./food") == ["icons", "food"]
    assert folder_parts("") == []


def test_family_in_folder_matches_prefix_and_exact() -> None:
    assert family_in_folder("icons/animals/cat", "icons/animals")
    assert family_in_folder("icons/animals", "icons/animals")
    assert not family_in_folder("icons/animals", "icons/animal")
    assert family_in_folder("icons/food/apple", "")


def test_folder_prefixes_note_kind_drops_family_dir() -> None:
    catalog = _catalog(
        [
            _family("cat", "icons/animals/cat"),
            _family("dog", "icons/animals/dog"),
            _family("apple", "icons/food/apple"),
            _family("loose", "icons/loose"),
        ]
    )
    assert catalog.folder_prefixes() == ["icons", "icons/animals", "icons/food"]


def test_folder_prefixes_flat_kind_keeps_file_parent() -> None:
    catalog = _catalog(
        [
            _family("star", "ui/actions", categories=["ui"]),
            _family("root", "", categories=["misc"]),
        ],
        kind="flat",
    )
    assert catalog.folder_prefixes() == ["ui", "ui/actions"]


def test_filter_icons_by_folder_prefix() -> None:
    catalog = _catalog(
        [
            _family("cat", "icons/animals/cat", categories=["animals"]),
            _family("apple", "icons/food/apple", categories=["food"]),
        ]
    )
    assert [icon.id for icon in catalog.filter_icons(folder="icons/animals")] == ["cat"]
    assert [icon.id for icon in catalog.filter_icons(category="food")] == ["apple"]
