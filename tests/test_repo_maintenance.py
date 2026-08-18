"""Tests for Vector Icons check and beautify/optimize helpers."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.repo_maintenance import (
    beautify_and_optimize_icons,
    check_icon_repo,
    is_family_prefixed_filename,
)

_MIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">'
    '<rect width="32" height="32" fill="#336699"></rect>'
    "</svg>"
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
        "license-url: https://example.com/license\n"
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


def test_is_family_prefixed_filename() -> None:
    assert is_family_prefixed_filename("building__garage.md", "building__garage")
    assert is_family_prefixed_filename("building__garage_01.svg", "building__garage")
    assert not is_family_prefixed_filename("featured-image.svg", "building__garage")
    assert not is_family_prefixed_filename("house.svg", "building__garage")


def test_check_icon_repo_accepts_matching_note(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    report = check_icon_repo(repo)
    assert "Filenames, folders, and categories match." in report
    assert "Notes: 1" in report


def test_check_icon_repo_reports_category_and_filename_issues(tmp_path: Path) -> None:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "furniture" / "building__garage"
    _write(note / "featured-image.svg")
    _write(note / "img" / "wrong.svg")
    (note / "building__garage.md").write_text(
        "---\ncategories:\n  - building\ntags:\n  - garage\nlang: en\n---\n\n# Garage\n",
        encoding="utf-8",
    )
    report = check_icon_repo(repo)
    assert "folder category `furniture` does not match family id prefix `building`" in report
    assert "filename does not start with family id `building__garage`" in report
    assert "YAML categories [building] do not include folder category `furniture`" in report


def test_check_icon_repo_reports_flat_note_without_category_folder(tmp_path: Path) -> None:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "building__garage"
    _write(note / "featured-image.svg")
    (note / "building__garage.md").write_text(
        "---\ncategories:\n  - building\nlang: en\n---\n\n# Garage\n",
        encoding="utf-8",
    )
    report = check_icon_repo(repo)
    assert "note should live in `icons/building/building__garage`" in report


def test_beautify_and_optimize_icons_rewrites_svg(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    svg = repo / "icons" / "building" / "building__garage" / "img" / "building__garage_01.svg"
    before = svg.read_text(encoding="utf-8")
    report = beautify_and_optimize_icons(repo)
    after = svg.read_text(encoding="utf-8")
    assert "Beautify Markdown" in report
    assert "Optimized 2 SVG file(s)." in report
    assert after.startswith("<svg")
    assert after != before or "rect" in after
