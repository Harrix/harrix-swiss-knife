"""Tests for Add Vector Image helpers and note/flat import paths."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.add_vector import (
    AddVectorStatus,
    collect_vector_sources,
    copy_vectors_to_flat_folder,
    create_note_from_meta,
    variant_dest_name,
)
from harrix_swiss_knife.apps.icons.add_vector_ai import parse_add_vector_ai_response
from harrix_swiss_knife.apps.icons.add_vector_meta import (
    NoteMeta,
    consensus_value,
    defaults_from_source_stem,
    extract_permalink_base,
    extract_permalink_source_base,
    join_permalink,
    permalink_suffixes,
    scan_repo_meta_defaults,
)
from harrix_swiss_knife.apps.icons.catalog import load_catalog, rebuild_catalog

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
    _write(note / "img" / "building__garage_01.svg")
    (note / "building__garage.md").write_text(
        "---\n"
        "date: 2020-07-19\n"
        "categories:\n"
        "  - building\n"
        "tags:\n"
        "  - garage\n"
        "author: Anton Sergienko\n"
        "author-email: anton.b.sergienko@gmail.com\n"
        "license: CC BY 4.0\n"
        "license-url: https://github.com/Harrix/Harrix-Vector-Icons/blob/main/LICENSE.md\n"
        "permalink: https://harrix.dev/en/icons/building/building__garage\n"
        "permalink-source: "
        "https://github.com/Harrix/Harrix-Vector-Icons/blob/main/icons/building/building__garage/building__garage.md\n"
        "lang: en\n"
        "---\n\n"
        "# Garage\n\n![Featured image](featured-image.svg)\n\n## Icons\n\n"
        "- ![building__garage_01](img/building__garage_01.svg)\n",
        encoding="utf-8",
    )
    return repo


def test_defaults_from_source_stem() -> None:
    family_id, title, category = defaults_from_source_stem("building__garage_black")
    assert family_id == "building__garage"
    assert title == "Garage"
    assert category == "building"


def test_permalink_helpers() -> None:
    assert extract_permalink_base("https://harrix.dev/en/icons/building/building__garage") == (
        "https://harrix.dev/en/icons/"
    )
    assert extract_permalink_source_base(
        "https://github.com/Harrix/Harrix-Vector-Icons/blob/main/icons/building/building__garage/building__garage.md"
    ) == ("https://github.com/Harrix/Harrix-Vector-Icons/blob/main/icons/")
    assert permalink_suffixes("building", "building__garage") == (
        "building/building__garage",
        "building/building__garage/building__garage.md",
    )
    assert permalink_suffixes("", "building__garage") == ("", "")
    assert join_permalink("https://harrix.dev/en/icons/", "building/building__garage") == (
        "https://harrix.dev/en/icons/building/building__garage"
    )
    assert consensus_value(["a", "a"]) == "a"
    assert consensus_value(["a", "b"]) == ""


def test_scan_repo_meta_defaults(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    defaults = scan_repo_meta_defaults(repo)
    assert defaults.author == "Anton Sergienko"
    assert defaults.license == "CC BY 4.0"
    assert defaults.permalink_base == "https://harrix.dev/en/icons/"
    assert defaults.permalink_source_base == "https://github.com/Harrix/Harrix-Vector-Icons/blob/main/icons/"
    assert "building" in defaults.categories
    assert "building__garage_01" in defaults.existing_variant_stems


def test_flat_copy_mixed_extensions(tmp_path: Path) -> None:
    dest = tmp_path / "flat"
    dest.mkdir()
    svg = tmp_path / "a.svg"
    ai = tmp_path / "b.ai"
    _write(svg)
    ai.write_bytes(b"%PDF-ai-fake")
    report = copy_vectors_to_flat_folder([svg, ai], dest_dir=dest, collision_policy="rename")
    assert any(item.status == AddVectorStatus.ADDED for item in report.results)
    assert (dest / "a.svg").is_file()
    assert (dest / "b.ai").is_file()


def test_create_note_from_meta_and_catalog_extensions(tmp_path: Path) -> None:
    repo = tmp_path / "Harrix-Vector-Icons"
    (repo / "icons").mkdir(parents=True)
    source = tmp_path / "building__house_black.svg"
    _write(source)
    meta = NoteMeta(
        family_id="building__house",
        title="House",
        date="2026-08-16",
        category="building",
        tags=["house", "дом"],
        author="Anton Sergienko",
        author_email="anton.b.sergienko@gmail.com",
        license="CC BY 4.0",
        license_url="https://example.com/license",
        permalink="https://harrix.dev/en/icons/building/building__house",
        permalink_source="https://github.com/example/blob/main/icons/building/building__house/building__house.md",
        lang="en",
        featured_name="featured-image.svg",
    )
    report = create_note_from_meta(source, repo_root=repo, meta=meta, rebuild=True)
    assert any(item.status == AddVectorStatus.CREATED_NOTE for item in report.results)
    note = repo / "icons" / "building" / "building__house"
    assert (note / "img" / "building__house_black.svg").is_file()
    assert (note / "featured-image.svg").is_file()
    md = (note / "building__house.md").read_text(encoding="utf-8")
    assert "permalink: https://harrix.dev/en/icons/building/building__house" in md
    assert "categories:\n  - building\n" in md
    assert "# House" in md

    # Non-SVG variant in catalog
    (note / "img" / "building__house.ai").write_bytes(b"%PDF-ai")
    catalog = rebuild_catalog(repo)
    family = next(icon for icon in catalog.icons if icon.id == "building__house")
    assert any(variant.file.endswith(".ai") for variant in family.variants)


def test_variant_dest_name() -> None:
    assert variant_dest_name(Path("building__garage_02.svg"), family_id="building__garage") == (
        "building__garage_02.svg"
    )
    assert variant_dest_name(Path("extra.svg"), family_id="building__garage") == "building__garage_extra.svg"


def test_collect_vector_sources(tmp_path: Path) -> None:
    folder = tmp_path / "pack"
    _write(folder / "one.svg")
    (folder / "two.pdf").write_bytes(b"%PDF")
    (folder / "skip.txt").write_text("x", encoding="utf-8")
    found = collect_vector_sources([folder])
    names = {path.name for path in found}
    assert names == {"one.svg", "two.pdf"}


def test_parse_add_vector_ai_response() -> None:
    parsed = parse_add_vector_ai_response(
        "filename: building__shed\nname: Shed\ncategory: building\ntags:\nshed\ngarage-shed\n"
    )
    assert parsed.filename == "building__shed"
    assert parsed.name == "Shed"
    assert parsed.category == "building"
    assert parsed.tags == ["shed", "garage-shed"]


def test_load_catalog_after_ai_featured(tmp_path: Path) -> None:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "ui" / "ui__button"
    note.mkdir(parents=True)
    (note / "featured-image.ai").write_bytes(b"%PDF-ai")
    (note / "img").mkdir()
    (note / "img" / "ui__button.ai").write_bytes(b"%PDF-ai")
    (note / "ui__button.md").write_text("---\ncategories: [ui]\nlang: en\n---\n\n# Button\n", encoding="utf-8")
    catalog = rebuild_catalog(repo)
    family = catalog.icons[0]
    assert family.featured == "featured-image.ai"
    assert family.variants[0].file == "img/ui__button.ai"
    loaded = load_catalog(repo)
    assert loaded.icons[0].featured == "featured-image.ai"
