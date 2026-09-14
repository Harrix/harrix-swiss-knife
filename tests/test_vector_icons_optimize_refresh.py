"""Tests for targeted catalog hash refresh after Optimize SVG."""

from __future__ import annotations

import json
from pathlib import Path

from harrix_swiss_knife.apps.icons.catalog import (
    IconCatalog,
    IconFamily,
    IconVariant,
    refresh_hashes_for_paths,
    write_catalog_json,
)


def _write_svg(path: Path, mark: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">'
        f'<rect width="24" height="24" fill="{mark}"/></svg>\n',
        encoding="utf-8",
    )


def test_refresh_hashes_for_paths_updates_only_touched_family(tmp_path: Path) -> None:
    note = tmp_path / "icons" / "building__garage"
    featured = note / "featured-image.svg"
    variant = note / "img" / "building__garage_01.svg"
    other_variant = note / "img" / "building__garage_02.svg"
    _write_svg(featured, "black")
    _write_svg(variant, "red")
    _write_svg(other_variant, "blue")

    family = IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=[],
        folder="icons/building__garage",
        featured="featured-image.svg",
        featured_hash="old-featured",
        variants=[
            IconVariant(file="img/building__garage_01.svg", name="building__garage_01", hash="old-01"),
            IconVariant(file="img/building__garage_02.svg", name="building__garage_02", hash="old-02"),
        ],
    )
    untouched = IconFamily(
        id="building__house",
        title="House",
        categories=["building"],
        tags=[],
        folder="icons/building__house",
        featured="featured-image.svg",
        featured_hash="keep-me",
        variants=[],
    )
    catalog = IconCatalog(version=1, generated_at="", icons=[family, untouched], repo_root=tmp_path, kind="note")

    affected = refresh_hashes_for_paths(catalog, [variant])
    assert [item.id for item in affected] == ["building__garage"]
    assert family.variants[0].hash != "old-01"
    assert family.variants[1].hash == "old-02"
    assert family.featured_hash == "old-featured"
    assert untouched.featured_hash == "keep-me"

    write_catalog_json(catalog)
    raw = json.loads((tmp_path / "catalog.json").read_text(encoding="utf-8"))
    garage = next(item for item in raw["icons"] if item["id"] == "building__garage")
    assert garage["variants"][0]["hash"] == family.variants[0].hash
    assert garage["featured_hash"] == "old-featured"
