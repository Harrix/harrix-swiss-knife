"""Tests for template field @subfolders link resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.template_parser import TemplateField, TemplateParser

if TYPE_CHECKING:
    from pathlib import Path


def test_list_path_subfolders_returns_sorted_folder_names(tmp_path: Path) -> None:
    (tmp_path / "Moscow").mkdir()
    (tmp_path / "SPb").mkdir()
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "readme.txt").write_text("x", encoding="utf-8")

    assert OnNewMarkdown._list_path_subfolders(tmp_path) == ["Moscow", "SPb"]


def test_resolve_field_link_options_turns_city_into_combobox(tmp_path: Path) -> None:
    (tmp_path / "Moscow").mkdir()
    fields = [
        TemplateField("City", "line", "{{City:line@subfolders}}", field_link=TemplateParser.FIELD_LINK_SUBFOLDERS)
    ]
    config = {"path_target": str(tmp_path)}

    OnNewMarkdown._resolve_field_link_options(fields, config)

    assert fields[0].field_type == "combobox"
    assert fields[0].options == ["Moscow"]
