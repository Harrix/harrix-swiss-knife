"""Tests for city_note path helpers in OnNewMarkdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.template_parser import TemplateParser

if TYPE_CHECKING:
    from pathlib import Path

COFFEE_TEMPLATE = """### {{Title:line@note_name}}: {{Score:float:10}}

{{Images:images@Title#1024}}

_{{Title:line}}_

- **City:** {{City:line@subfolders}}
- **Address:** {{Address:line}}
- **Coordinates:** {{Coordinates:coordinates}}
- **Web:** <{{Web:line}}>
- **Date:** {{Date:date}}
- **Comments:** {{Comments:multiline}}
"""


def test_sanitize_note_stem_replaces_spaces_and_preserves_hyphens() -> None:
    assert OnNewMarkdown._sanitize_note_stem("Flat white") == "Flat-white"
    assert OnNewMarkdown._sanitize_note_stem("Double-B") == "Double--B"


def test_sanitize_folder_name_removes_invalid_characters() -> None:
    assert OnNewMarkdown._sanitize_folder_name("Moscow") == "Moscow"
    assert OnNewMarkdown._sanitize_folder_name('St. "Petersburg"') == "St. _Petersburg_"


def test_template_path_layout_detects_modes() -> None:
    assert OnNewMarkdown._template_path_layout({"path_target": "D:/Notes/Coffee/"}) == "year_file"
    assert OnNewMarkdown._template_path_layout({"path_target": "D:/Notes/Coffee.md"}) == "single_file"
    assert (
        OnNewMarkdown._template_path_layout({"path_target": "D:/Notes/Coffee/", "path_layout": "city_note"})
        == "city_note"
    )


def test_city_note_field_names_from_template_links() -> None:
    fields, _ = TemplateParser.parse_template(COFFEE_TEMPLATE)
    city_field, name_field = OnNewMarkdown._city_note_field_names(fields, {})
    assert city_field == "City"
    assert name_field == "Title"


def test_resolve_city_note_paths_builds_named_folder_layout(tmp_path: Path) -> None:
    config = {"path_target": str(tmp_path / "Coffee")}
    fields, _ = TemplateParser.parse_template(COFFEE_TEMPLATE)
    values = {"City": "Moscow", "Title": "Flat white"}
    city_dir, note_md, note_dir, note_stem = OnNewMarkdown._resolve_city_note_paths(fields, config, values)
    assert city_dir == tmp_path / "Coffee" / "Moscow"
    assert note_stem == "Flat-white"
    assert note_md == h.md.named_note_md_path(city_dir, note_stem)
    assert note_dir == note_md.parent


def test_list_city_note_entries_finds_notes_in_city_folders(tmp_path: Path) -> None:
    root = tmp_path / "Coffee"
    moscow = root / "Moscow" / "Flat-white"
    moscow.mkdir(parents=True)
    (moscow / "Flat-white.md").write_text("# test\n", encoding="utf-8")
    spb = root / "SPb" / "Double-B"
    spb.mkdir(parents=True)
    (spb / "Double-B.md").write_text("# test2\n", encoding="utf-8")

    entries = OnNewMarkdown._list_city_note_entries(root)
    labels = [label for label, _ in entries]
    assert "Moscow / Flat-white" in labels
    assert "SPb / Double-B" in labels


def test_parse_block_round_trip_for_single_city_note_file() -> None:
    fields, _ = TemplateParser.parse_template(COFFEE_TEMPLATE)
    values = {
        "Title": "Flat white",
        "Score": "9",
        "Images": "img/a.jpg",
        "City": "Moscow",
        "Address": "Tverskaya St, 12",
        "Coordinates": "55.7558, 37.6173",
        "Web": "https://example.com",
        "Date": "2025-06-01",
        "Comments": "Nice",
    }
    content = TemplateParser.fill_template(COFFEE_TEMPLATE, values)
    parsed = TemplateParser.parse_block(COFFEE_TEMPLATE, content, fields)
    assert parsed is not None
    assert parsed["City"] == "Moscow"
    assert parsed["Title"] == "Flat white"
    assert parsed["Images"] == "img/a.jpg"
