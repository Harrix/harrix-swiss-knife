"""Tests for collecting SVG paths on icon families."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.catalog import (
    IconFamily,
    IconVariant,
    family_has_svg_files,
    family_svg_paths,
)


def _family(*, featured: str = "featured-image.svg", variants: list[IconVariant] | None = None) -> IconFamily:
    return IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=["garage"],
        folder="icons/building/building__garage",
        featured=featured,
        featured_hash="abc",
        variants=variants or [],
    )


def test_family_has_svg_files() -> None:
    assert family_has_svg_files(_family())
    assert family_has_svg_files(
        _family(featured="featured-image.ai", variants=[IconVariant(file="img/a.svg", name="a", hash="1")]),
    )
    assert not family_has_svg_files(_family(featured="featured-image.ai", variants=[]))


def test_family_svg_paths_include_featured_and_variants(tmp_path: Path) -> None:
    note = tmp_path / "icons" / "building" / "building__garage"
    featured = note / "featured-image.svg"
    variant = note / "img" / "building__garage_01.svg"
    featured.parent.mkdir(parents=True, exist_ok=True)
    variant.parent.mkdir(parents=True, exist_ok=True)
    featured.write_text("<svg/>", encoding="utf-8")
    variant.write_text("<svg/>", encoding="utf-8")
    (note / "featured-image.ai").write_bytes(b"ai")
    family = _family(
        variants=[IconVariant(file="img/building__garage_01.svg", name="01", hash="1")],
    )
    all_paths = family_svg_paths(family, tmp_path)
    assert featured.resolve() in {path.resolve() for path in all_paths}
    assert variant.resolve() in {path.resolve() for path in all_paths}
    variants_only = family_svg_paths(family, tmp_path, include_featured=False)
    assert [path.resolve() for path in variants_only] == [variant.resolve()]
