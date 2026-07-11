"""Tests for city_note path helpers in OnNewMarkdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.template_entry_browser import TemplateExistingEntry
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
- **Date:** {{Date:date@Images}}
- **Last visit:** {{DateLast:date@Images!}}
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


def test_build_entry_browser_groups_for_city_note_layout(tmp_path: Path) -> None:
    root = tmp_path / "Coffee"
    moscow = root / "Moscow" / "Flat-white"
    moscow.mkdir(parents=True)
    (moscow / "Flat-white.md").write_text("# test\n", encoding="utf-8")

    config = {"path_target": str(root), "path_layout": "city_note"}
    groups = OnNewMarkdown._build_entry_browser_groups(config, COFFEE_TEMPLATE)
    assert len(groups) == 1
    assert groups[0].label == "Moscow"
    assert len(groups[0].entries) == 1
    assert groups[0].entries[0].kind == "city_note"
    assert groups[0].entries[0].label == "Flat-white"


def test_build_entry_browser_groups_for_single_file_layout(tmp_path: Path) -> None:
    events_md = tmp_path / "Events.md"
    events_md.write_text(
        "## 2025\n\n### Concert A: 10\n\nText A\n\n### Concert B: 9\n\nText B\n",
        encoding="utf-8",
    )
    template = "### {{Title:line}}: {{Score:float:10}}\n\n{{Comments:multiline}}\n"
    config = {"path_target": str(events_md)}
    groups = OnNewMarkdown._build_entry_browser_groups(config, template)
    assert len(groups) == 1
    assert groups[0].label == "Events.md"
    titles = [entry.label for entry in groups[0].entries]
    assert "Concert A: 10" in titles
    assert "Concert B: 9" in titles


def test_load_template_entry_field_values_for_city_note(tmp_path: Path) -> None:
    note_dir = tmp_path / "Moscow" / "Flat-white"
    note_dir.mkdir(parents=True)
    fields, _ = TemplateParser.parse_template(COFFEE_TEMPLATE)
    values = {
        "Title": "Flat white",
        "Score": "9",
        "Images": "",
        "City": "Moscow",
        "Address": "Main st",
        "Coordinates": "55.7558, 37.6173",
        "Web": "https://example.com",
        "Date": "2025-06-01",
        "Comments": "Nice",
    }
    content = TemplateParser.fill_template(COFFEE_TEMPLATE, values)
    note_md = note_dir / "Flat-white.md"
    note_md.write_text(content, encoding="utf-8")
    entry = TemplateExistingEntry(kind="city_note", label="Flat-white", note_md=str(note_md))
    loaded = OnNewMarkdown._load_template_entry_field_values(entry, COFFEE_TEMPLATE, fields)
    assert loaded is not None
    assert loaded["Title"] == "Flat white"
    assert loaded["City"] == "Moscow"


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
