"""Tests for adding SVG files into Vector Icons note folders."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.icons.add_svgs import (
    AddSvgStatus,
    add_svgs_to_repo,
    build_jobs,
    discover_source_svgs,
    jobs_with_content_collisions,
    unique_variant_name,
)
from harrix_swiss_knife.apps.icons.catalog import load_catalog
from harrix_swiss_knife.apps.icons.family_id import family_id_from_stem

_MIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#336699"/></svg>'
)
_OTHER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">'
    '<circle cx="16" cy="16" r="12" fill="#990000"/></svg>'
)


def _write(path: Path, text: str = _MIN_SVG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo_with_note(tmp_path: Path) -> Path:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "building" / "building__garage"
    _write(note / "featured-image.svg")
    _write(note / "img" / "building__garage_01.svg")
    (note / "building__garage.md").write_text(
        "---\ncategories: [building]\ntags: [garage]\nlang: en\n---\n\n"
        "# Garage\n\n![Featured image](featured-image.svg)\n\n## Icons\n\n"
        "- ![building__garage_01](img/building__garage_01.svg)\n",
        encoding="utf-8",
    )
    return repo


def test_family_id_from_stem_strips_variants() -> None:
    assert family_id_from_stem("building__garage_black_01") == "building__garage"
    assert family_id_from_stem("clothes__suit") == "clothes__suit"


def test_discover_source_svgs_skips_repo_icons_tree(tmp_path: Path) -> None:
    repo = _repo_with_note(tmp_path)
    inbox = repo / "incoming"
    _write(inbox / "building__garage_02.svg")
    found = discover_source_svgs(repo)
    assert any(path.name == "building__garage_02.svg" for path in found)
    assert not any(
        "icons" in path.parts and path.name.endswith(".svg") and "incoming" not in path.parts for path in found
    )


def test_add_svgs_creates_note_and_optimizes(tmp_path: Path) -> None:
    repo = tmp_path / "Harrix-Vector-Icons"
    (repo / "icons").mkdir(parents=True)
    source = tmp_path / "inbox"
    _write(source / "fiction_robot__bender_01.svg")

    report = add_svgs_to_repo(source, repo_root=repo, collision_policy="rename", rebuild=True)
    statuses = {item.status for item in report.results}
    assert AddSvgStatus.CREATED_NOTE in statuses
    assert AddSvgStatus.ADDED in statuses
    note = repo / "icons" / "fiction_robot" / "fiction_robot__bender"
    assert (note / "img" / "fiction_robot__bender_01.svg").is_file()
    assert (note / "featured-image.svg").is_file()
    md = (note / "fiction_robot__bender.md").read_text(encoding="utf-8")
    assert "author: Anton Sergienko" in md
    assert "permalink-source:" in md
    assert "fiction_robot__bender_01.svg" in md
    catalog = load_catalog(repo)
    assert any(icon.id == "fiction_robot__bender" for icon in catalog.icons)


def test_collision_rename_and_replace(tmp_path: Path) -> None:
    repo = _repo_with_note(tmp_path)
    source = tmp_path / "inbox"
    _write(source / "building__garage_01.svg", _OTHER_SVG)

    jobs = build_jobs(discover_source_svgs(source), repo_root=repo)
    assert jobs_with_content_collisions(jobs)

    renamed = add_svgs_to_repo(source, repo_root=repo, collision_policy="rename", rebuild=False)
    assert any(item.status == AddSvgStatus.RENAMED for item in renamed.results)
    note_img = repo / "icons" / "building" / "building__garage" / "img"
    assert (note_img / "building__garage_01_new.svg").is_file()
    assert (note_img / "building__garage_01.svg").read_text(encoding="utf-8") == _MIN_SVG

    _write(source / "building__garage_01.svg", _OTHER_SVG)
    replaced = add_svgs_to_repo(source, repo_root=repo, collision_policy="replace", rebuild=True)
    assert any(item.status == AddSvgStatus.REPLACED for item in replaced.results)
    # Optimized content may differ from raw input, but must not stay the old rectangle-only SVG.
    assert (note_img / "building__garage_01.svg").read_text(encoding="utf-8") != _MIN_SVG


def test_skip_identical_hash(tmp_path: Path) -> None:
    repo = _repo_with_note(tmp_path)
    source = tmp_path / "inbox"
    _write(source / "building__garage_01.svg", _MIN_SVG)
    report = add_svgs_to_repo(source, repo_root=repo, collision_policy="replace", rebuild=False)
    assert any(item.status == AddSvgStatus.SKIPPED_SAME for item in report.results)


def test_unique_variant_name(tmp_path: Path) -> None:
    img = tmp_path / "img"
    img.mkdir()
    (img / "icon_new.svg").write_text(_MIN_SVG, encoding="utf-8")
    assert unique_variant_name(img, "icon") == "icon_new2.svg"
